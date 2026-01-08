import streamlit as st
import os

def create_global_sidebar(df):
    """
    Recreates the high-end V1 sidebar logic for the current suite.
    """
    st.sidebar.title("💎 AjayDataLabs")
    st.sidebar.markdown("*Enterprise BI & Logistics*")
    st.sidebar.divider()

    st.sidebar.header("🗓️ Global Filters")
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()

    date_range = st.sidebar.date_input(
        "Select Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Recreating your V1 'Methodology' section
    st.sidebar.markdown("---")
    with st.sidebar.expander("🛠️ Methodology"):
        st.write(f"**Viewing:** {date_range}")
        st.write("**Models:** XGBoost, RFM Clustering")
        st.write("**Engine:** Apache Parquet Gold Layer")

    return date_range