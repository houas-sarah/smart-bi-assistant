"""
AI-Powered Text-to-SQL Engine using an ONLINE LLM (Hugging Face)
No local model needed – the LLM is called via HTTP.
"""

import os
import re
import sqlite3
from typing import Tuple, Optional, List

import pandas as pd
import requests
from dotenv import load_dotenv

from database import NorthwindDB

# ============================================================================
# CONFIG
# ============================================================================

load_dotenv()  # Load variables from .env if present

HF_API_KEY = os.getenv("HF_API_KEY")  # You must set this in a .env file
HF_MODEL_NAME = os.getenv(
    "HF_MODEL_NAME",
    "mistralai/Mistral-7B-Instruct-v0.2"  # default model (can be changed)
)

if HF_API_KEY is None:
    print("⚠️  HF_API_KEY is not set. Create a .env file with HF_API_KEY=your_token")

# Create a single DB instance
db = NorthwindDB("northwind.db")


# ============================================================================
# HELPER: GET DATABASE SCHEMA (FOR THE PROMPT)
# ============================================================================

def get_schema_description(db_path: str = "northwind.db") -> str:
    """
    Introspect the SQLite database to build a small schema description
    (tables + columns). This is sent to the LLM so it knows what exists.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_lines = []

    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        # Skip SQLite internal tables
        if table.startswith("sqlite_"):
            continue

        # Sécuriser le nom de la table (quotes + escape des apostrophes)
        safe_table = table.replace("'", "''")
        cursor.execute(f"PRAGMA table_info('{safe_table}');")

        columns = [row[1] for row in cursor.fetchall()]  # column names
        schema_lines.append(f"{table}: {', '.join(columns)}")

    conn.close()
    return "\n".join(schema_lines)



SCHEMA_DESCRIPTION = get_schema_description("northwind.db")


# ============================================================================
# CLEANING & VALIDATION HELPERS
# ============================================================================

def clean_sql(sql_text: str) -> str:
    """Extract a clean SQL SELECT query from the LLM output."""
    if not sql_text:
        return ""

    sql = sql_text.strip()

    # Remove markdown code fences
    sql = re.sub(r"^```(sql)?", "", sql, flags=re.IGNORECASE | re.MULTILINE)
    sql = re.sub(r"```$", "", sql, flags=re.MULTILINE).strip()

    # Keep only the part starting at SELECT and ending at the first semicolon
    match = re.search(r"select.+?;", sql, flags=re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(0).strip()
    else:
        # No explicit SELECT ... ; found
        return ""

    return sql


def is_valid_sql(sql: str) -> bool:
    """
    Very simple security check:
    - Only allow SELECT queries
    - Forbid other dangerous commands
    """
    if not sql:
        return False

    lowered = sql.strip().lower()
    if not lowered.startswith("select"):
        return False

    forbidden = ["drop ", "delete ", "update ", "insert ", "alter "]
    if any(word in lowered for word in forbidden):
        return False

    return True


# ============================================================================
# ONLINE LLM CALL (HUGGING FACE INFERENCE API)
# ============================================================================

def call_llm_for_sql(question: str) -> str:
    """
    Call an online LLM on Hugging Face Router (hf-inference) to generate SQL.
    Uses the OpenAI-compatible /v1/chat/completions endpoint.
    """
    if not HF_API_KEY:
        raise RuntimeError("HF_API_KEY is missing. Set it in your .env file.")

    prompt = f"""
You are an assistant that converts natural language business questions into **valid SQLite SELECT queries**.

DATABASE SCHEMA:
{SCHEMA_DESCRIPTION}

RULES:
- Use only the tables and columns from the schema above.
- Return exactly ONE SQL query.
- The query MUST be a valid SQLite SELECT statement.
- Do NOT explain anything, do NOT add comments.
- Do NOT wrap the query in markdown code fences.
- Always start with SELECT and end with a semicolon.

Question: {question}

SQL query:
""".strip()

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }

    # ex: HF_MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    # le router attend "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B:hf-inference"
    base_model = HF_MODEL_NAME or "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    model_name = f"{base_model}:hf-inference"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.1,
        "stream": False,
    }

    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"LLM API error ({response.status_code}): {response.text}"
        )

    data = response.json()
    try:
        raw_output = data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected LLM response format: {data}")

    return raw_output



# ============================================================================
# MAIN FUNCTIONS USED BY THE STREAMLIT APP
# ============================================================================

def text_to_sql(question: str) -> str:
    """
    Take the user question and return a cleaned, validated SQL query.
    """
    raw = call_llm_for_sql(question)
    sql = clean_sql(raw)

    if not is_valid_sql(sql):
        raise RuntimeError(
            f"The LLM did not produce a valid SQL SELECT query.\nRaw output was:\n{raw}"
        )

    return sql


def execute_and_explain(question: str) -> Tuple[Optional[str], Optional[pd.DataFrame], str]:
    """
    High-level helper used by app.py:
    - Convert question -> SQL
    - Run SQL on the Northwind DB
    - Return (sql, results_df, explanation_message)
    """
    try:
        sql = text_to_sql(question)
    except Exception as e:
        return None, None, f"❌ Unable to generate a valid SQL query: {e}"

    results_df, error = db.execute_query(sql)

    if error:
        return sql, None, f"⚠️ SQL generated, but the database returned an error: {error}"

    if results_df is None or len(results_df) == 0:
        return sql, results_df, "✅ Query executed successfully, but no rows matched the criteria."

    return sql, results_df, f"✅ Query executed successfully and returned {len(results_df)} row(s)."


def get_example_questions() -> List[str]:
    """
    Example BI questions to display in the Streamlit sidebar.
    """
    return [
        "How many customers are there?",
        "List the top 10 customers by total revenue.",
        "Which countries have the most customers?",
        "What are the top 5 best selling products?",
        "Show me the total sales per country.",
        "Which employees have generated the most revenue?",
        "What is the average order value per customer?",
        "Which products are low in stock?",
        "Show monthly sales totals.",
    ]


# Small CLI test (optional)
if __name__ == "__main__":
    print("🔍 Testing the online Text-to-SQL engine...")
    q = "What are the top 5 customers by revenue?"
    sql, df, msg = execute_and_explain(q)
    print("SQL:", sql)
    print("Message:", msg)
    if df is not None:
        print(df.head())
