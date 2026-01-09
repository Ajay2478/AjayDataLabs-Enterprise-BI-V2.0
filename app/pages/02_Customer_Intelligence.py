import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import requests
from io import BytesIO
from dotenv import load_dotenv

# 1. PATHING & ENVIRONMENT (Must come first for Cloud compatibility)
load_dotenv()
# Dynamically locate the root directory to access 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import your shared UI and Analytics
from src.ui_components import create_global_sidebar
from src.analytics import CustomerAnalytics

# 2. PAGE CONFIG
st.set_page_config(page_title="Customer Intelligence", layout="wide")

# 3. CLOUD-AWARE DATA ENGINE
@st.cache_data
def load_cloud_data():
    """
    Handles data loading for both local and production environments.
    """
    # Attempt Local Load (Your PC)
    local_path = os.getenv("PROCESSED_DATA_PATH")
    if local_path and os.path.exists(local_path):
        return pd.read_parquet(local_path)
    
    # CLOUD PRODUCTION: Raw Stream from Dropbox
    cloud_url = "https://www.dropbox.com/scl/fi/5daz0xt5dthm24hbyioxb/cleaned_data.parquet?rlkey=wvkn08glbo3ofur47l77fy978&st=9jbpru00&dl=1"
    
    try:
        # Direct binary stream for memory efficiency
        response = requests.get(cloud_url)
        response.raise_for_status() 
        return pd.read_parquet(BytesIO(response.content))
    except Exception as e:
        st.error("⚠️ Customer Data Sync Failed.")
        st.sidebar.error(f"Error: {e}")
        return pd.DataFrame()

# 4. INITIALIZE DATA & ANALYTICS
raw_df = load_cloud_data()

@st.cache_data
def get_rfm_data(_df): 
    """
    Generates RFM segments using the provided DataFrame.
    The underscore tells Streamlit not to hash the massive DataFrame object.
    """
    # Uses the updated flexible class constructor
    analyzer = CustomerAnalytics(df=_df) 
    return analyzer.generate_rfm()

if not raw_df.empty:
    with st.spinner("Analyzing 1M+ rows of customer behavior..."):
        rfm_df = get_rfm_data(raw_df)

    # 5. PERSISTENT SIDEBAR
    date_range = create_global_sidebar(raw_df)

    # 6. PAGE CONTENT
    st.title("🎯 Customer Intelligence Lab")
    st.markdown("---")

    # --- 7. THE CIRCLE (Donut Intelligence) ---
    st.subheader("Customer Segmentation Distribution")

    segment_counts = rfm_df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']

    # Create the Executive Donut Chart with divergent colors
    fig = px.pie(
        segment_counts, 
        values='Count', 
        names='Segment', 
        hole=0.5, 
        color_discrete_sequence=px.colors.diverging.RdYlGn[::-1], 
        title="Market Share by Customer Segment"
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        template="plotly_dark",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, l=20, r=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 8. DEEP DIVE LOGIC ---
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

    st.success(f"📈 Strategy Insight: We have identified {len(champions)} Champions driving revenue.")
else:
    st.warning("Please wait for data synchronization...")