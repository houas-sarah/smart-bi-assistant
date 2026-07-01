"""
Smart BI Query Assistant - Enhanced Enterprise UI
Professional styling with modern design patterns
"""

import streamlit as st
import pandas as pd
from query_engine import get_example_questions
from database import NorthwindDB
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION & THEMING
# ============================================================================

st.set_page_config(
    page_title="Smart BI Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "**Smart BI Assistant** - Master's Thesis Project | ESTIN 2025"
    }
)

# ============================================================================
# CUSTOM CSS - Professional Dark Theme with Gradients
# ============================================================================

st.markdown("""
<style>
    /* Root Variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --accent: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --border: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
    }
    
    /* Main Container Styling */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
        color: var(--text-primary);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid var(--border);
    }
    
    /* Header Styling */
    .header-container {
        background: linear-gradient(90deg, #6366f1 0%, #ec4899 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        background: linear-gradient(90deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Input/Search Box Styling */
    .search-container {
        position: relative;
        margin: 2rem 0;
    }
    
    .stTextInput > div > div > input {
        background: var(--card-bg) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border: 2px solid var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #4338ca 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Card/Container Styling */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card:hover {
        border: 1px solid var(--primary);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }
    
    /* Success/Error Message Styling */
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--success);
        padding: 1rem;
        border-radius: 8px;
        color: #d1fae5;
        margin: 1rem 0;
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--danger);
        padding: 1rem;
        border-radius: 8px;
        color: #fecaca;
        margin: 1rem 0;
    }
    
    .info-message {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        color: #c7d2fe;
        margin: 1rem 0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--card-bg);
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: var(--text-secondary);
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        background: var(--card-bg) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: var(--card-bg) !important;
    }
    
    /* Metric Styling */
    .stMetric {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    
    /* Example Questions Box */
    .examples-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .example-item {
        background: var(--card-bg);
        border-left: 3px solid var(--primary);
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .example-item:hover {
        background: rgba(99, 102, 241, 0.1);
        transform: translateX(5px);
    }
    
    /* Footer Styling */
    .footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--card-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'history' not in st.session_state:
    st.session_state.history = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

@st.cache_resource
def init_db():
    """Initialize database connection"""
    return NorthwindDB()

db = init_db()

# ============================================================================
# HEADER SECTION
# ============================================================================

st.markdown("""
<div class="header-container">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 2.5rem;">📊</div>
        <div>
            <h1 class="header-title">Smart BI Assistant</h1>
            <p class="header-subtitle">Natural Language Business Intelligence System</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# How it works info box
st.info("💡 **How it works:** Type your business question → AI generates SQL → Get instant results with visualizations", 
        icon="ℹ️")

# ============================================================================
# MAIN QUERY INTERFACE
# ============================================================================

col1, col2 = st.columns([0.85, 0.15])

with col1:
    user_question = st.text_input(
        "Ask your business question:",
        placeholder="E.g., 'What are the top 5 customers by revenue?'",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("🔍 Search", use_container_width=True)

# ============================================================================
# EXAMPLE QUESTIONS SIDEBAR
# ============================================================================

st.sidebar.markdown("### 📌 Quick Examples")

example_questions = get_example_questions()

for i, example in enumerate(example_questions):
    if st.sidebar.button(example, key=f"example_{i}", use_container_width=True):
        user_question = example
        search_button = True

# ============================================================================
# QUERY EXECUTION SECTION
# ============================================================================

if search_button and user_question:
    st.session_state.query_count += 1
    
    with st.spinner("🔄 Processing your question..."):
        try:
            # Generate and execute SQL
            from query_engine import execute_and_explain
            import time
            
            start_time = time.time()
            sql, results_df, explanation = execute_and_explain(user_question)
            elapsed_time = time.time() - start_time
            
            # Add to history
            st.session_state.history.append({
                'question': user_question,
                'timestamp': datetime.now(),
                'time': elapsed_time
            })
            
            # Display Results Section
            st.markdown("---")
            
            # Explanation Banner
            st.markdown(f"""
            <div class="success-message">
                ✅ {explanation}
            </div>
            """, unsafe_allow_html=True)
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Results", "🔧 SQL Query", "📈 Analytics"])
            
            # TAB 1: RESULTS
            with tab1:
                if results_df is not None and len(results_df) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📋 Records", len(results_df))
                    with col2:
                        st.metric("⏱️ Query Time", f"{elapsed_time:.2f}s")
                    with col3:
                        st.metric("📑 Columns", len(results_df.columns))
                    with col4:
                        st.metric("✨ Query ID", f"#{st.session_state.query_count}")
                    
                    st.markdown("#### Data Table")
                    
                    # Display dataframe with enhanced styling
                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=False,
                        column_config={
                            col: st.column_config.Column(width="medium")
                            for col in results_df.columns
                        }
                    )
                    
                    # Download option
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download as CSV",
                        data=csv,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.markdown("""
                    <div class="info-message">
                        ℹ️ No results found for this query.
                    </div>
                    """, unsafe_allow_html=True)
            
            # TAB 2: SQL QUERY
            with tab2:
                st.markdown("#### Generated SQL Query")
                st.code(sql, language="sql", line_numbers=True)
                
                # Copy button
                if st.button("📋 Copy SQL", use_container_width=True):
                    st.success("SQL copied to clipboard!")
            
            # TAB 3: ANALYTICS (for numeric data)
            with tab3:
                if results_df is not None and len(results_df) > 0:
                    # Get numeric columns
                    numeric_cols = results_df.select_dtypes(include=['number']).columns.tolist()
                    
                    if numeric_cols:
                        st.markdown("#### Data Visualization")
                        
                        # Auto-detect chart type based on data
                        if len(results_df) <= 20 and len(numeric_cols) <= 3:
                            fig = px.bar(
                                results_df,
                                x=results_df.columns[0],
                                y=numeric_cols[0] if numeric_cols else results_df.columns[1],
                                title="Data Visualization",
                                color_discrete_sequence=['#6366f1'],
                                template="plotly_dark"
                            )
                            
                            fig.update_layout(
                                hovermode='x unified',
                                plot_bgcolor='rgba(30,41,59,0.5)',
                                paper_bgcolor='rgba(15,23,42,1)',
                                font=dict(color='#f1f5f9'),
                                title_font_size=18,
                                xaxis_title_font_size=14,
                                yaxis_title_font_size=14
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("📊 Visualization not available for this data structure.")
                    else:
                        st.info("📊 No numeric columns found for visualization.")
                else:
                    st.info("ℹ️ No data to visualize.")
        
        except Exception as e:
            st.markdown(f"""
            <div class="error-message">
                ❌ Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.stop()

# ============================================================================
# QUERY HISTORY SIDEBAR
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 📜 Query History")

if st.session_state.history:
    for i, entry in enumerate(reversed(st.session_state.history[-5:])):
        with st.sidebar.expander(f"Query {len(st.session_state.history) - i}"):
            st.write(f"**Question:** {entry['question']}")
            st.write(f"**Time:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Duration:** {entry['time']:.2f}s")
else:
    st.sidebar.write("*No queries yet. Start asking!*")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="footer">
    <div style="margin-bottom: 1rem;">
        <strong>Smart BI Assistant</strong> | Business Intelligence System
    </div>
    <div>
        Master's Thesis Project - ESTIN 2025<br>
        Sarah Houas | s_houas@estin.dz
    </div>
</div>
""", unsafe_allow_html=True)
