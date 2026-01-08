import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from src.ui_components import create_global_sidebar

load_dotenv()

st.set_page_config(page_title="Logistics Intelligence", layout="wide")

@st.cache_data
def load_data():
    path = os.getenv("PROCESSED_DATA_PATH")
    return pd.read_parquet(path)

df = load_data()
date_range = create_global_sidebar(df)

st.title("🌍 Geospatial Logistics Intelligence")
st.markdown("---")

# --- 1. Map Logic ---
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

# --- 2. Top Markets Table ---
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