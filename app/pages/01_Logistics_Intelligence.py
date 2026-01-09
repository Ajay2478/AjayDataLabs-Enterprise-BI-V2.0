import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import requests
from io import BytesIO
from dotenv import load_dotenv

# 1. PATH FIX (Critical for Cloud Deployment)
# Tells the app to look one level up for the 'src' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ui_components import create_global_sidebar

load_dotenv()

st.set_page_config(page_title="Logistics Intelligence", layout="wide")

# 2. CLOUD-AWARE DATA ENGINE
@st.cache_data
def load_data():
    # Attempt Local Load (Your PC)
    local_path = os.getenv("PROCESSED_DATA_PATH")
    if local_path and os.path.exists(local_path):
        return pd.read_parquet(local_path)
    
    # CLOUD PRODUCTION: Raw Stream from Dropbox
    cloud_url = "https://www.dropbox.com/scl/fi/5daz0xt5dthm24hbyioxb/cleaned_data.parquet?rlkey=wvkn08glbo3ofur47l77fy978&st=9jbpru00&dl=1"
    
    try:
        # Stream the parquet file directly into memory
        response = requests.get(cloud_url)
        response.raise_for_status() 
        return pd.read_parquet(BytesIO(response.content))
    except Exception as e:
        st.error("⚠️ Logistics Data Sync Failed.")
        st.sidebar.error(f"Technical Log: {e}")
        return pd.DataFrame()

df = load_data()

# 3. SIDEBAR & UI
if not df.empty:
    date_range = create_global_sidebar(df)

    st.title("🌍 Geospatial Logistics Intelligence")
    st.markdown("---")

    # --- 4. Map Logic ---
    st.subheader("Global Revenue Distribution")

    # Group by country
    country_data = df.groupby('Country')['Line_Total'].sum().reset_index()

    # Create the Map
    fig = px.choropleth(
        country_data,
        locations="Country",
        locationmode='country names',
        color="Line_Total",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Revenue Hotspots by Country"
    )

    fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Top Markets Table ---
    st.subheader("Market Performance Breakdown")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(country_data.sort_values(by='Line_Total', ascending=False), use_container_width=True)

    with col2:
        st.info("""
        **Senior Insight:**
        The UK remains the primary revenue driver. For a 'Top 1%' logistics strategy, 
        the focus should be on reducing international shipping friction in 
        emerging European markets like Germany and France.
        """)
else:
    st.warning("Data load failed. Please check the cloud source.")