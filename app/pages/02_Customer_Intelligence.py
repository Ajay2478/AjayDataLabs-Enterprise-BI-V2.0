import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
from dotenv import load_dotenv

# 1. PATHING & ENVIRONMENT (Must come first)
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# Import your shared UI and Analytics
from src.ui_components import create_global_sidebar
from src.analytics import CustomerAnalytics

# 2. PAGE CONFIG
st.set_page_config(page_title="Customer Intelligence", layout="wide")

# 3. DATA ENGINE
@st.cache_data
def get_rfm_data():
    analyzer = CustomerAnalytics()
    return analyzer.generate_rfm()

# Load the core dataframe for the sidebar and the RFM for the page
# Note: Ensure PROCESSED_DATA_PATH is in your .env
raw_df = pd.read_parquet(os.getenv("PROCESSED_DATA_PATH"))
rfm_df = get_rfm_data()

# 4. PERSISTENT SIDEBAR (The V1 Restoration)
# This call ensures your sidebar stays the same across all pages
date_range = create_global_sidebar(raw_df)

# 5. PAGE CONTENT
st.title("🎯 Customer Intelligence Lab")
st.markdown("---")

# --- 6. THE CIRCLE (Donut Intelligence) ---
st.subheader("Customer Segmentation Distribution")

# Prepare counts for the visual
segment_counts = rfm_df['Segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Count']

# Create the Executive Donut Chart
fig = px.pie(
    segment_counts, 
    values='Count', 
    names='Segment', 
    hole=0.5, 
    color_discrete_sequence=px.colors.diverging.RdYlGn[::-1], 
    title="Market Share by Customer Segment"
)

# Professional UI Styling
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(
    template="plotly_dark",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=50, l=20, r=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# --- 7. DEEP DIVE LOGIC ---
st.divider()
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚠️ High-Priority: At Risk")
    at_risk = rfm_df[rfm_df['Segment'] == 'At Risk'].sort_values(by='Monetary', ascending=False)
    st.dataframe(at_risk[['Recency', 'Frequency', 'Monetary']].head(10), use_container_width=True)
    st.caption("Action: Send win-back discount codes immediately.")

with col2:
    st.subheader("🏆 The Champions")
    champions = rfm_df[rfm_df['Segment'] == 'Champions'].sort_values(by='Monetary', ascending=False)
    st.dataframe(champions[['Recency', 'Frequency', 'Monetary']].head(10), use_container_width=True)
    st.caption("Action: Enroll in VIP early-access program.")

# 8. Strategic Conclusion
st.success(f"📈 Strategy Insight: We have identified {len(champions)} Champions driving significant revenue velocity.")