"""
Tests for the text-to-SQL engine helpers (query_engine).

Only the pure/offline helpers are tested here — the live LLM call
(`call_llm_for_sql`) is intentionally not exercised so the suite runs
without a network connection or API key.
"""

import query_engine as qe


# --- clean_sql --------------------------------------------------------------

def test_clean_sql_strips_markdown_fences():
    raw = "```sql\nSELECT * FROM Customers;\n```"
    assert qe.clean_sql(raw) == "SELECT * FROM Customers;"


def test_clean_sql_extracts_select_from_noise():
    raw = "Sure! Here is your query:\nSELECT Country FROM Customers;\nHope it helps."
    assert qe.clean_sql(raw) == "SELECT Country FROM Customers;"


def test_clean_sql_returns_empty_when_no_select():
    assert qe.clean_sql("I cannot help with that.") == ""
    assert qe.clean_sql("") == ""


# --- is_valid_sql -----------------------------------------------------------

def test_is_valid_sql_accepts_select():
    assert qe.is_valid_sql("SELECT * FROM Customers") is True


def test_is_valid_sql_rejects_non_select():
    assert qe.is_valid_sql("PRAGMA table_info(Customers)") is False
    assert qe.is_valid_sql("") is False


def test_is_valid_sql_rejects_forbidden_keywords():
    assert qe.is_valid_sql("SELECT 1; DROP TABLE Customers") is False
    assert qe.is_valid_sql("SELECT 1; DELETE FROM Orders") is False


# --- schema introspection ---------------------------------------------------

def test_schema_description_lists_core_tables():
    schema = qe.get_schema_description("northwind.db")
    for table in ("Customers", "Orders", "Products"):
        assert table in schema


def test_schema_description_skips_empty_tables():
    # CustomerDemographics has 0 rows in the bundled DB and must be omitted.
    schema = qe.get_schema_description("northwind.db")
    assert "CustomerDemographics" not in schema


# --- example questions ------------------------------------------------------

def test_example_questions_non_empty():
    questions = qe.get_example_questions()
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(isinstance(q, str) and q for q in questions)
