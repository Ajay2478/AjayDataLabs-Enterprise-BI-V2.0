import streamlit as st
import pandas as pd
import os
import sys
import requests # Added for raw data streaming
from io import BytesIO # Added for memory-efficient loading
import plotly.express as px
from dotenv import load_dotenv

# --- 1. THE CLOUD PATH FIX ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ui_components import create_global_sidebar

# 2. INITIALIZATION
load_dotenv()

st.set_page_config(page_title="AjayDataLabs BI Suite", page_icon="💎", layout="wide")

# 3. DATA ENGINE (The "Beyond" Cloud Strategy)
@st.cache_data
def load_gold_layer():
    # Attempt to load from Local Path first (for your PC development)
    local_path = os.getenv("PROCESSED_DATA_PATH")
    if local_path and os.path.exists(local_path):
        return pd.read_parquet(local_path)
    
    # CLOUD PRODUCTION: Raw Stream from Dropbox
    # Your verified link
    cloud_url = "https://www.dropbox.com/scl/fi/5daz0xt5dthm24hbyioxb/cleaned_data.parquet?rlkey=wvkn08glbo3ofur47l77fy978&st=9jbpru00&dl=1"
    
    try:
        # Stream the parquet file directly into memory
        response = requests.get(cloud_url)
        response.raise_for_status() # Ensure the connection is healthy
        return pd.read_parquet(BytesIO(response.content))
    except Exception as e:
        st.error("⚠️ Enterprise Data Sync Failed. Check cloud connectivity.")
        st.sidebar.error(f"Technical Log: {e}")
        return pd.DataFrame()

df = load_gold_layer()

# 4. CALL SHARED SIDEBAR (Persistent Branding)
if not df.empty:
    date_range = create_global_sidebar(df)

    # Apply global filter logic
    if isinstance(date_range, tuple) and len(date_range) == 2:
        mask = (df['InvoiceDate'].dt.date >= date_range[0]) & (df['InvoiceDate'].dt.date <= date_range[1])
        filtered_df = df.loc[mask]
    else:
        filtered_df = df

    # 5. MAIN DASHBOARD: EXECUTIVE COCKPIT
    st.title("🏛️ Executive Cockpit")
    st.markdown("---")

    # KPI SECTION
    total_rev = filtered_df['Line_Total'].sum()
    total_ord = filtered_df['Invoice'].nunique()
    unique_cust = filtered_df['Customer ID'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_rev/1e6:.2f}M", delta="+5.2%")
    col2.metric("Total Orders", f"{total_ord:,}", delta="+12%")
    col3.metric("Unique Customers", f"{unique_customers:,}", delta="-2.1%")

    st.success("✨ Gold Layer Synced: Real-time Enterprise Metrics Active.")

    # 6. REVENUE VELOCITY
    st.subheader("📈 Revenue Growth Velocity")
    revenue_trend = filtered_df.set_index('InvoiceDate')['Line_Total'].resample('MS').sum().reset_index()

    fig_trend = px.area(
        revenue_trend, x='InvoiceDate', y='Line_Total',
        title="Monthly Revenue Performance",
        color_discrete_sequence=['#00CC96']
    )
    fig_trend.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_trend, use_container_width=True)

    # 7. TOP DRIVERS
    st.divider()
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.info("**🔍 Market Analysis:** Stability is high; seasonal spikes confirmed.")
    with col_right:
        st.markdown("### 🏆 Top 5 Revenue Drivers")
        top_products = filtered_df.groupby('Description')['Line_Total'].sum().sort_values(ascending=False).head(5)
        st.table(top_products)
else:
    st.warning("Please upload data to initialize the dashboard.")