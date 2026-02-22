import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_and_clean_data
import numpy as np

# Page config
st.set_page_config(page_title="Loan Defaulters Insights", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for strict dark mode & premium aesthetic
st.markdown("""
<style>
    /* Force Dark Theme */
    :root {
        --background-color: #0B0E14;
        --secondary-bg: #151A23;
        --text-color: #E2E8F0;
        --accent-color: #3182CE;
        --border-color: #2D3748;
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F7FAFC !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    h1 { font-size: 2.5rem; border-bottom: 2px solid var(--border-color); padding-bottom: 15px; margin-bottom: 30px;}
    h2 { font-size: 1.8rem; margin-top: 1.5rem; color: #CBD5E0 !important;}
    h3 { font-size: 1.4rem; color: #A0AEC0 !important;}
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-bg) !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.6);
        border-color: #4A5568;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: var(--secondary-bg);
        border-radius: 8px 8px 0px 0px;
        border: 1px solid var(--border-color);
        border-bottom: none;
        color: var(--text-color);
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-color) !important;
        color: white !important;
        font-weight: 600;
        border-color: var(--accent-color);
    }
    
    /* Hide some Streamlit default branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Alerts */
    .stAlert {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid #E53E3E !important;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Define dark theme for all plotly charts globally
import plotly.io as pio
pio.templates.default = "plotly_dark"
PLOTLY_BG = 'rgba(0,0,0,0)'
COLOR_MAP = {'Repayer (0)': '#38B2AC', 'Defaulter (1)': '#F56565'}

# Title
st.title("🏦 Loan Defaulters Analytical Dashboard")

# Load data
with st.spinner("Processing Dataset & Computing Aggregations..."):
    app_df, prev_app_df, merged_df = load_and_clean_data()

# Check if data exists
if app_df is None or merged_df is None:
    st.error("""
        ### 🚨 Missing Data Files
        Please place `application_data.csv` and `previous_application.csv` in the root directory.
    """)
    st.stop()

# Prepare common data structures for speed
if 'TARGET_STR' not in app_df.columns:
    app_df['TARGET_STR'] = app_df['TARGET'].replace({0: 'Repayer (0)', 1: 'Defaulter (1)'})
    
# Function to safely sample large dataframes for Plotly rendering
def get_plot_sample(df, max_samples=10000):
    if len(df) > max_samples:
        return df.sample(n=max_samples, random_state=42)
    return df

# Helper to apply standard plotly layout
def apply_dark_layout(fig):
    fig.update_layout(
        paper_bgcolor=PLOTLY_BG,
        plot_bgcolor=PLOTLY_BG,
        font=dict(color='#E2E8F0'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# --- Layout: Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Business Overview", 
    "👥 Demographics", 
    "💰 Financials", 
    "📈 Correlations",
    "💡 Actionable Insights"
])

# -------------------------------------------------------------------------------------------------
# TAB 1: Business Overview
# -------------------------------------------------------------------------------------------------
with tab1:
    st.header("Executive Summary")
    st.markdown("Understand the core distribution and high-level behavioral attributes of the loan applicants.")

    total_apps = len(app_df)
    defaulter_rate = (app_df['TARGET'].sum() / total_apps) * 100
    avg_loan_amt = app_df['AMT_CREDIT'].mean()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Applicants", f"{total_apps:,.0f}")
    m2.metric("Defaulter Rate", f"{defaulter_rate:.2f}%")
    m3.metric("Avg Loan Amount ($)", f"${avg_loan_amt:,.0f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Target Distribution")
        # Aggregated pie chart is fast
        target_counts = app_df['TARGET_STR'].value_counts().reset_index()
        target_counts.columns = ['Client Type', 'Count']
        fig = px.pie(target_counts, names='Client Type', values='Count', color='Client Type',
                     color_discrete_map=COLOR_MAP, hole=0.45)
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

    with col2:
        st.subheader("Contract Types by Client")
        # Aggregation before plotting
        contract_agg = app_df.groupby(['NAME_CONTRACT_TYPE', 'TARGET_STR']).size().reset_index(name='Count')
        fig = px.bar(contract_agg, x='NAME_CONTRACT_TYPE', y='Count', color='TARGET_STR', barmode='group',
                     color_discrete_map=COLOR_MAP,
                     labels={'NAME_CONTRACT_TYPE': 'Contract Type', 'TARGET_STR': 'Client Type'})
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)


# -------------------------------------------------------------------------------------------------
# TAB 2: Demographic Insights
# -------------------------------------------------------------------------------------------------
with tab2:
    st.header("Demographic Profiling")
    st.markdown("Analyzing how factors like age, education, and occupation influence default rates.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Age Distribution by Default Status")
        # Sample age data to speed up histogram rendering
        sample_age_df = get_plot_sample(app_df, 15000)
        fig = px.histogram(sample_age_df, x="DAYS_BIRTH", color="TARGET_STR", marginal="box", 
                   nbins=40, color_discrete_map=COLOR_MAP, opacity=0.7, barmode='overlay',
                   labels={'DAYS_BIRTH': 'Age (Days)', 'TARGET_STR': 'Client Type'})
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

    with col2:
        st.subheader("Default Rates by Education Level")
        ed_pct = app_df.groupby('NAME_EDUCATION_TYPE')['TARGET'].mean().reset_index()
        ed_pct['Default Rate (%)'] = ed_pct['TARGET'] * 100
        ed_pct = ed_pct.sort_values('Default Rate (%)', ascending=False)
        fig = px.bar(ed_pct, x='NAME_EDUCATION_TYPE', y='Default Rate (%)', color='Default Rate (%)',
                     color_continuous_scale='Reds', labels={'NAME_EDUCATION_TYPE': 'Education Type'})
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)
        
    st.subheader("Default Rates by Occupation Type")
    occ_pct = app_df.groupby('OCCUPATION_TYPE')['TARGET'].mean().reset_index()
    occ_pct['Default Rate (%)'] = occ_pct['TARGET'] * 100
    occ_pct = occ_pct.sort_values('Default Rate (%)', ascending=False)
    fig = px.bar(occ_pct, x='OCCUPATION_TYPE', y='Default Rate (%)', color='Default Rate (%)',
                 color_continuous_scale='Reds', labels={'OCCUPATION_TYPE': 'Occupation'})
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

# -------------------------------------------------------------------------------------------------
# TAB 3: Financial Analysis
# -------------------------------------------------------------------------------------------------
with tab3:
    st.header("Financial Metrics")
    st.markdown("Investigating the impact of income, credit amounts, and historical application behaviour.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Income Distribution (Filtered < 500k)")
        inc_filter = app_df['AMT_INCOME_TOTAL'] < 500000
        sample_inc_df = get_plot_sample(app_df[inc_filter], 15000)
        fig = px.histogram(sample_inc_df, x='AMT_INCOME_TOTAL', color='TARGET_STR', nbins=40, barmode='overlay',
                           color_discrete_map=COLOR_MAP, opacity=0.7,
                           labels={'AMT_INCOME_TOTAL': 'Total Income Amount'})
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

    with col2:
        st.subheader("Credit Amount Distribution")
        sample_credit_df = get_plot_sample(app_df, 15000)
        fig = px.histogram(sample_credit_df, x='AMT_CREDIT', color='TARGET_STR', nbins=40, barmode='overlay',
                           color_discrete_map=COLOR_MAP, opacity=0.7,
                           labels={'AMT_CREDIT': 'Total Credit Amount'})
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)
        
    st.subheader("Previous Applications: Contract Status vs Default")
    # Add TARGET_STR to merged_df if missing
    if 'TARGET_STR' not in merged_df.columns and 'TARGET' in merged_df.columns:
        merged_df['TARGET_STR'] = merged_df['TARGET'].replace({0: 'Repayer (0)', 1: 'Defaulter (1)'})
    # Using merged_df to look at previous application behaviour
    merged_agg = merged_df.groupby(['NAME_CONTRACT_STATUS', 'TARGET_STR']).size().reset_index(name='Count')
    fig = px.bar(merged_agg, x='NAME_CONTRACT_STATUS', y='Count', color='TARGET_STR', barmode='group',
                 color_discrete_map=COLOR_MAP, log_y=True,
                 labels={'NAME_CONTRACT_STATUS': 'Previous Contract Status'})
    st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

# -------------------------------------------------------------------------------------------------
# TAB 4: Correlation Findings
# -------------------------------------------------------------------------------------------------
with tab4:
    st.header("Multivariate Correlations")
    st.markdown("Understanding complex interactions between numeric attributes using optimized subsets of the data.")
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("Credit vs Goods Price (Sampled)")
        # Sample down heavily to avoid massive browser lag
        sampled_scatter_df = get_plot_sample(app_df, 3000)
        fig = px.scatter(sampled_scatter_df, x='AMT_CREDIT', y='AMT_GOODS_PRICE', color='TARGET_STR',
                         color_discrete_map=COLOR_MAP, opacity=0.7,
                         labels={'AMT_CREDIT':'Credit Amount', 'AMT_GOODS_PRICE': 'Goods Price'})
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

    with col2:
        st.subheader("Numeric Feature Heatmap (Defaulters)")
        # Filter defaulters and compute corr matrix (fast operation)
        defaulters = app_df[app_df['TARGET'] == 1]
        num_cols = ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE', 'DAYS_BIRTH', 'DAYS_EMPLOYED']
        corr_matrix = defaulters[num_cols].corr()
        
        fig = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r")
        st.plotly_chart(apply_dark_layout(fig), use_container_width=True)

# -------------------------------------------------------------------------------------------------
# TAB 5: Actionable Insights
# -------------------------------------------------------------------------------------------------
with tab5:
    st.header("💡 Actionable Insights & Data Explorer")
    st.markdown("Dynamic facts extracted from the dataset regarding highest default probabilities.")
    
    st.markdown("### Top Risk Categories")
    
    # Precompute top risk categories for quick display
    top_occ = occ_pct.iloc[0]
    top_ed = ed_pct.iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Highest Risk Occupation:** {top_occ['OCCUPATION_TYPE']} at **{top_occ['Default Rate (%)']:.1f}%** default rate.")
        
    with c2:
        st.error(f"**Highest Risk Education:** {top_ed['NAME_EDUCATION_TYPE']} at **{top_ed['Default Rate (%)']:.1f}%** default rate.")

    st.markdown("---")
    st.markdown("### Discover Defaulter Profiles")
    st.markdown("Use the filters below to browse a subset of actual clients who defaulted on their loans.")
    
    # Filter controls
    defaulters_only = app_df[app_df['TARGET'] == 1]
    
    scol1, scol2 = st.columns(2)
    with scol1:
        selected_occ = st.selectbox("Filter by Occupation", options=["All"] + list(defaulters_only['OCCUPATION_TYPE'].unique()))
    with scol2:
        selected_gender = st.radio("Filter by Gender", options=["All", "M", "F", "XNA"], horizontal=True)
        
    # Apply filters
    filtered_df = defaulters_only.copy()
    if selected_occ != "All":
        filtered_df = filtered_df[filtered_df['OCCUPATION_TYPE'] == selected_occ]
    if selected_gender != "All":
        filtered_df = filtered_df[filtered_df['CODE_GENDER'] == selected_gender]
        
    disp_cols = ['SK_ID_CURR', 'CODE_GENDER', 'FLAG_OWN_CAR', 'CNT_CHILDREN', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'NAME_EDUCATION_TYPE', 'OCCUPATION_TYPE']
    
    st.write(f"Showing **{len(filtered_df):,}** defaulters matching criteria.")
    # Show dataframe
    st.dataframe(filtered_df[disp_cols].head(100), use_container_width=True)

