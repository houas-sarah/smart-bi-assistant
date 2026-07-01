"""
Smart BI Assistant — Streamlit interface
Editorial dark theme: warm neutrals, one confident accent, real typography.
"""

import os
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# On Streamlit Community Cloud there is no .env file — credentials come from
# st.secrets. Mirror them into environment variables so query_engine (which
# reads os.getenv) works identically whether run locally or deployed.
try:
    for _key in ("HF_API_KEY", "HF_MODEL_NAME"):
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = str(st.secrets[_key])
except Exception:
    pass

from query_engine import execute_and_explain, get_example_questions
from database import NorthwindDB

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart BI Assistant",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Smart BI Assistant · Master's Thesis · ESTIN 2025"},
)

# Signature chart palette (reused everywhere for consistency)
PALETTE = ["#ff6a45", "#f4b740", "#58d6b0", "#6aa6ff", "#c084fc", "#f472b6"]

# ---------------------------------------------------------------------------
# Design system (CSS)
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg:       #0e0e12;
    --panel:    #16161c;
    --panel-2:  #1c1c24;
    --line:     #2a2a33;
    --line-soft:#22222a;
    --ink:      #ece9e3;
    --muted:    #928e86;
    --faint:    #67635c;
    --coral:    #ff6a45;
    --coral-2:  #ff8a6a;
    --amber:    #f4b740;
    --mint:     #58d6b0;
}

/* Base ------------------------------------------------------------------ */
html, body, [class*="css"], .stApp, input, textarea, button {
    font-family: 'Inter', -apple-system, sans-serif;
}
.stApp {
    background:
        radial-gradient(1100px 520px at 78% -8%, rgba(255,106,69,0.10), transparent 60%),
        radial-gradient(900px 500px at 8% 4%, rgba(88,214,176,0.05), transparent 55%),
        var(--bg);
    color: var(--ink);
}
.block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 1180px; }

h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.01em; }
a { color: var(--coral-2); }
hr { border-color: var(--line-soft); }

/* Kicker / mono labels -------------------------------------------------- */
.kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase;
    color: #ff9270; margin: 0 0 0.7rem 2px; text-shadow: 0 0 24px rgba(255,106,69,0.35);
}
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--muted); margin: 1.6rem 0 0.7rem; display: flex; align-items: center; gap: .6rem;
}
.section-label .n { color: var(--coral); font-weight: 600; }
.section-label::after { content:""; flex:1; height:1px; background: var(--line-soft); }

/* Header ---------------------------------------------------------------- */
.wordmark {
    font-size: 2.7rem; font-weight: 700; margin: 0; line-height: 1.05; color: var(--ink);
}
.wordmark .mk { color: var(--coral); }
.tagline { color: var(--muted); font-size: 1.02rem; margin: .5rem 0 1rem; max-width: 560px; }

.chips { display:flex; gap:.5rem; flex-wrap:wrap; }
.chip {
    font-family:'JetBrains Mono', monospace; font-size:.72rem; color: var(--muted);
    background: var(--panel); border:1px solid var(--line);
    padding:.32rem .7rem; border-radius: 999px; display:inline-flex; align-items:center; gap:.4rem;
}
.chip .d { width:6px; height:6px; border-radius:50%; background: var(--mint); box-shadow:0 0 8px var(--mint); }

/* Flow strip ------------------------------------------------------------ */
.flow { display:flex; align-items:stretch; gap:.6rem; margin:1.4rem 0 .4rem; flex-wrap:wrap; }
.flow-step {
    flex:1; min-width:150px; background: var(--panel); border:1px solid var(--line);
    border-radius:12px; padding:.85rem 1rem; display:flex; gap:.7rem; align-items:center;
}
.flow-step .fn {
    font-family:'JetBrains Mono', monospace; font-size:.8rem; color: var(--coral);
    border:1px solid var(--line); border-radius:8px; width:26px; height:26px;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.flow-step .ft { font-weight:600; font-size:.9rem; color: var(--ink); }
.flow-step .fd { font-size:.78rem; color: var(--faint); }

/* Inputs ---------------------------------------------------------------- */
.stTextInput > div > div > input {
    background: var(--panel) !important; border:1px solid var(--line) !important;
    border-radius:12px !important; padding: .95rem 1.1rem !important;
    color: var(--ink) !important; font-size:1.02rem !important;
}
.stTextInput > div > div > input::placeholder { color: var(--faint) !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--coral) !important;
    box-shadow: 0 0 0 3px rgba(255,106,69,0.14) !important;
}

/* Buttons — primary = coral, everything else = ghost ------------------- */
.stButton > button, .stDownloadButton > button {
    background: var(--panel); color: var(--ink);
    border:1px solid var(--line); border-radius:11px;
    padding:.7rem 1rem; font-weight:500; font-size:.9rem;
    transition: all .18s ease; width:100%; text-align:left;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--coral); color:#fff; background: var(--panel-2);
}
.stButton > button[kind="primary"] {
    background: var(--coral); color:#1a0f0b; border:1px solid var(--coral);
    font-weight:600; text-align:center;
}
.stButton > button[kind="primary"]:hover {
    background: var(--coral-2); border-color: var(--coral-2); color:#1a0f0b;
    box-shadow: 0 6px 22px rgba(255,106,69,0.28);
}

/* Sidebar --------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: #101015; border-right:1px solid var(--line-soft);
}
[data-testid="stSidebar"] .stButton > button { font-size:.82rem; padding:.55rem .8rem; }
.side-h {
    font-family:'JetBrains Mono', monospace; font-size:.72rem; letter-spacing:.18em;
    text-transform:uppercase; color: var(--faint); margin:1.3rem 0 .6rem;
}

/* Result banner --------------------------------------------------------- */
.banner {
    display:flex; align-items:center; gap:.7rem; background: var(--panel);
    border:1px solid var(--line); border-left:3px solid var(--mint);
    padding:.85rem 1.1rem; border-radius:10px; color: var(--ink);
    font-size:.92rem; margin:.6rem 0 1.2rem;
}
.banner.warn { border-left-color: var(--amber); }
.banner.err  { border-left-color: var(--coral); }
.banner .bd { width:7px; height:7px; border-radius:50%; background: var(--mint); flex-shrink:0; }
.banner.warn .bd { background: var(--amber); }
.banner.err .bd  { background: var(--coral); }

/* Metrics --------------------------------------------------------------- */
[data-testid="stMetric"] {
    background: var(--panel); border:1px solid var(--line); border-radius:12px;
    padding:1rem 1.1rem; position:relative; overflow:hidden;
}
[data-testid="stMetric"]::before {
    content:""; position:absolute; top:0; left:0; width:100%; height:2px; background: var(--coral);
    opacity:.7;
}
[data-testid="stMetricLabel"] {
    font-family:'JetBrains Mono', monospace; font-size:.68rem !important;
    letter-spacing:.12em; text-transform:uppercase; color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family:'JetBrains Mono', monospace; font-weight:600; color: var(--ink) !important;
}

/* Tabs ------------------------------------------------------------------ */
.stTabs [data-baseweb="tab-list"] { gap:.4rem; background:transparent; border-bottom:1px solid var(--line-soft); }
.stTabs [data-baseweb="tab"] {
    background:transparent; color: var(--muted); border-radius:8px 8px 0 0;
    padding:.55rem 1.1rem; font-family:'JetBrains Mono', monospace; font-size:.8rem; letter-spacing:.05em;
}
.stTabs [aria-selected="true"] { color: var(--coral) !important; border-bottom:2px solid var(--coral); }

/* Dataframe ------------------------------------------------------------- */
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; }

/* Code console ---------------------------------------------------------- */
.console-bar {
    display:flex; align-items:center; gap:.45rem; padding:.55rem .9rem;
    background: var(--panel-2); border:1px solid var(--line); border-bottom:none;
    border-radius:12px 12px 0 0;
}
.console-bar .dot { width:11px; height:11px; border-radius:50%; }
.console-bar .t {
    margin-left:.6rem; font-family:'JetBrains Mono', monospace; font-size:.72rem; color: var(--faint);
}
.stCodeBlock { border-radius:0 0 12px 12px !important; }

/* Empty / info ---------------------------------------------------------- */
.note {
    background: var(--panel); border:1px solid var(--line); border-radius:12px;
    padding:1.4rem; color: var(--muted); font-size:.92rem; text-align:center;
}

/* Footer ---------------------------------------------------------------- */
.foot {
    margin-top:3rem; padding-top:1.4rem; border-top:1px solid var(--line-soft);
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem;
    font-family:'JetBrains Mono', monospace; font-size:.74rem; color: var(--faint);
}
.foot .a { color: var(--muted); }

/* Scrollbar ------------------------------------------------------------- */
::-webkit-scrollbar { width:9px; height:9px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--line); border-radius:6px; }
::-webkit-scrollbar-thumb:hover { background: var(--coral); }

#MainMenu, footer, header [data-testid="stToolbar"] { visibility:hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# State & data
# ---------------------------------------------------------------------------

st.session_state.setdefault("history", [])
st.session_state.setdefault("query_count", 0)
st.session_state.setdefault("question_input", "")
st.session_state.setdefault("run_requested", False)
st.session_state.setdefault("current", None)  # last result: dict or None


def request_query(question: str):
    """Button callback: drop a suggestion into the search box and run it.

    Runs *before* the rerun, so the text input picks up the new value when it
    renders — this is why clicking a suggestion now fills the search field.
    """
    st.session_state.question_input = question
    st.session_state.run_requested = True


@st.cache_resource
def init_db():
    return NorthwindDB()


db = init_db()


def run_edited_sql():
    """Button callback: re-run the SQL the user edited by hand.

    The edited query goes through the SAME read-only validation as generated
    SQL, so a human can verify/fix the AI's query without any risk of a write
    operation slipping through.
    """
    edited = st.session_state.get("sql_editor", "").strip()
    question = (st.session_state.current or {}).get("question", "Edited query")
    if not edited:
        return

    ok, msg = db.validate_query(edited)
    if not ok:
        st.session_state.current = {
            "question": question, "sql": edited, "df": None,
            "explanation": f"⚠️ Rejected — {msg.strip()}", "elapsed": 0.0, "edited": True,
        }
        return

    start = time.time()
    df, err = db.execute_query(edited)
    elapsed = time.time() - start
    if err:
        explanation, df = f"⚠️ SQL error: {err}", None
    elif df is None or len(df) == 0:
        explanation = "✅ Query executed, but no rows matched."
    else:
        explanation = f"✅ Query executed and returned {len(df)} row(s)."

    st.session_state.current = {
        "question": question, "sql": edited, "df": df,
        "explanation": explanation, "elapsed": elapsed, "edited": True,
    }


# ---------------------------------------------------------------------------
# Chart helper
# ---------------------------------------------------------------------------

def build_chart(df: pd.DataFrame):
    """Pick a sensible chart for the result set, styled to the theme."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols or len(df.columns) < 2 or len(df) < 2 or len(df) > 40:
        return None

    x_col = next((c for c in df.columns if c not in numeric_cols), df.columns[0])
    y_col = next((c for c in numeric_cols if c != x_col), numeric_cols[0])

    # Time-ish x-axis -> line, otherwise bar.
    temporal = any(k in str(x_col).lower() for k in ("month", "date", "year", "day", "time"))
    chart_title = f"{y_col} by {x_col}"
    if temporal:
        fig = px.line(df, x=x_col, y=y_col, markers=True,
                      color_discrete_sequence=[PALETTE[0]], title=chart_title)
    else:
        fig = px.bar(df, x=x_col, y=y_col,
                     color_discrete_sequence=[PALETTE[0]], title=chart_title)

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#ece9e3", size=13),
        title=dict(text=chart_title, font=dict(family="Space Grotesk", size=16, color="#ece9e3")),
        margin=dict(l=10, r=10, t=52, b=10),
        xaxis=dict(gridcolor="#22222a", title_font_size=12),
        yaxis=dict(gridcolor="#22222a", title_font_size=12),
        hoverlabel=dict(bgcolor="#16161c", bordercolor="#2a2a33", font_family="JetBrains Mono"),
    )
    fig.update_traces(marker_line_width=0)
    return fig


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="kicker">Natural-language analytics</div>
<h1 class="wordmark">Smart BI <span class="mk">/ Assistant</span></h1>
<p class="tagline">Ask a business question in plain English — get the SQL, the data,
and a chart without writing a single query.</p>
<div class="chips">
    <span class="chip"><span class="d"></span> Connected</span>
    <span class="chip">Northwind</span>
    <span class="chip">SQLite</span>
    <span class="chip">16,282 orders · 93 customers · 77 products</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="flow">
    <div class="flow-step"><span class="fn">1</span><div><div class="ft">Ask</div><div class="fd">Plain-English question</div></div></div>
    <div class="flow-step"><span class="fn">2</span><div><div class="ft">Translate</div><div class="fd">LLM writes safe SQL</div></div></div>
    <div class="flow-step"><span class="fn">3</span><div><div class="ft">Explore</div><div class="fd">Table, chart & CSV</div></div></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Query interface
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label"><span class="n">01</span> Ask a question</div>', unsafe_allow_html=True)

col_q, col_b = st.columns([0.82, 0.18])
with col_q:
    user_question = st.text_input(
        "question",
        key="question_input",
        placeholder="e.g. Which products generate the most revenue?",
        label_visibility="collapsed",
    )
with col_b:
    search_button = st.button("Run query", type="primary", use_container_width=True)

# Quick suggestion pills (main area)
suggestions = [
    "Top 5 customers by revenue",
    "Show monthly sales totals",
    "Best selling products",
    "Total sales per country",
]
pill_cols = st.columns(len(suggestions))
for i, (pc, text) in enumerate(zip(pill_cols, suggestions)):
    with pc:
        st.button(text, key=f"pill_{i}", use_container_width=True,
                  on_click=request_query, args=(text,))

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.markdown('<div class="kicker">Smart BI</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="side-h">Example questions</div>', unsafe_allow_html=True)

for i, example in enumerate(get_example_questions()):
    st.sidebar.button(example, key=f"ex_{i}", use_container_width=True,
                      on_click=request_query, args=(example,))

st.sidebar.markdown('<div class="side-h">Recent queries</div>', unsafe_allow_html=True)
if st.session_state.history:
    for i, entry in enumerate(reversed(st.session_state.history[-6:])):
        n = len(st.session_state.history) - i
        with st.sidebar.expander(f"#{n} · {entry['question'][:26]}"):
            st.caption(entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
            st.write(entry["question"])
            st.caption(f"{entry['time']:.2f}s")
else:
    st.sidebar.caption("Nothing yet — ask your first question.")

# ---------------------------------------------------------------------------
# Execution & results
# ---------------------------------------------------------------------------

run_now = search_button or st.session_state.run_requested
st.session_state.run_requested = False

# --- Run a new question -> store the result in session state --------------
if run_now and user_question:
    st.session_state.query_count += 1
    with st.spinner("Translating your question into SQL…"):
        try:
            start = time.time()
            sql, results_df, explanation = execute_and_explain(user_question)
            elapsed = time.time() - start
        except Exception as exc:  # unexpected failure
            sql, results_df, explanation, elapsed = None, None, f"❌ Error: {exc}", 0.0

    st.session_state.history.append(
        {"question": user_question, "timestamp": datetime.now(), "time": elapsed}
    )
    st.session_state.current = {
        "question": user_question, "sql": sql, "df": results_df,
        "explanation": explanation, "elapsed": elapsed, "edited": False,
    }
    # Seed the editable SQL box with the freshly generated query.
    st.session_state.sql_editor = sql or ""

# --- Render the current result (survives reruns / SQL edits) --------------
cur = st.session_state.current
if cur:
    sql, results_df, explanation, elapsed = cur["sql"], cur["df"], cur["explanation"], cur["elapsed"]

    st.markdown('<div class="section-label"><span class="n">02</span> Result</div>', unsafe_allow_html=True)

    tone = "err" if explanation.strip().startswith("❌") else "warn" if explanation.strip().startswith("⚠️") else ""
    clean_msg = explanation.lstrip("✅⚠️❌ ").strip()
    edited_tag = " · edited by you" if cur.get("edited") else ""
    st.markdown(
        f'<div class="banner {tone}"><span class="bd"></span>{clean_msg}{edited_tag}</div>',
        unsafe_allow_html=True,
    )

    tab_table, tab_sql, tab_chart = st.tabs(["TABLE", "SQL", "CHART"])

    with tab_table:
        if results_df is not None and len(results_df) > 0:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rows", len(results_df))
            m2.metric("Columns", len(results_df.columns))
            m3.metric("Time", f"{elapsed:.2f}s")
            m4.metric("Query", f"#{st.session_state.query_count}")

            st.dataframe(results_df, use_container_width=True, hide_index=True)

            st.download_button(
                "Download CSV",
                data=results_df.to_csv(index=False),
                file_name=f"query_{datetime.now():%Y%m%d_%H%M%S}.csv",
                mime="text/csv",
            )
        else:
            st.markdown('<div class="note">No rows matched this question.</div>', unsafe_allow_html=True)

    with tab_sql:
        if sql:
            st.markdown(
                '<div class="console-bar">'
                '<span class="dot" style="background:#ff5f56"></span>'
                '<span class="dot" style="background:#ffbd2e"></span>'
                '<span class="dot" style="background:#27c93f"></span>'
                '<span class="t">generated_query.sql</span></div>',
                unsafe_allow_html=True,
            )
            st.code(sql, language="sql")

            with st.expander("✏️  Verify & re-run this query"):
                st.caption(
                    "The AI can misread a question, so review the SQL and edit it if "
                    "needed. Only read-only SELECT / WITH queries are allowed."
                )
                st.text_area("edit-sql", key="sql_editor", height=170,
                             label_visibility="collapsed")
                st.button("Run edited SQL", type="primary", on_click=run_edited_sql)
        else:
            st.markdown('<div class="note">No SQL was generated for this question.</div>', unsafe_allow_html=True)

    with tab_chart:
        fig = build_chart(results_df) if results_df is not None else None
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                '<div class="note">No chart for this shape of data — '
                'charts appear for small, aggregated result sets.</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="foot">
    <span>Smart BI Assistant · Natural-language business intelligence</span>
</div>
""",
    unsafe_allow_html=True,
)
