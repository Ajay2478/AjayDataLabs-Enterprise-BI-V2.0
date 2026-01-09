import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import requests
from io import BytesIO
from dotenv import load_dotenv

# 1. PATHING
load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.ui_components import create_global_sidebar

# 2. LOCAL ANALYTICS CLASS (The Nuclear Option)
# We define it here to bypass the broken 'src' cache on the cloud
class CloudCustomerAnalytics:
    def __init__(self, df):
        self.df = df
            
    def generate_rfm(self):
        if self.df.empty:
            return pd.DataFrame()
        df = self.df
        snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
        rfm = df.groupby('Customer ID').agg({
            'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
            'Invoice': 'nunique',
            'Line_Total': 'sum'
        }).rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'Line_Total': 'Monetary'})
        rfm = rfm[rfm.index.notnull()]
        
        # Scoring
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str)
        
        segs = {
            r'[1-2][1-2]': 'Hibernating', r'[1-2][3-4]': 'At Risk', r'[1-2]5': 'Can\'t Lose Them',
            r'3[1-2]': 'About to Sleep', r'33': 'Need Attention', r'[3-4][4-5]': 'Loyalists',
            r'41': 'Promising', r'51': 'New Customers', r'[4-5][2-3]': 'Potential Loyalists',
            r'5[4-5]': 'Champions'
        }
        rfm['Segment'] = rfm['RFM_Score'].replace(segs, regex=True)
        return rfm

# 3. PAGE CONFIG
st.set_page_config(page_title="Customer Intelligence", layout="wide")

# 4. DATA LOADING
@st.cache_data
def load_cloud_data():
    cloud_url = "https://www.dropbox.com/scl/fi/5daz0xt5dthm24hbyioxb/cleaned_data.parquet?rlkey=wvkn08glbo3ofur47l77fy978&st=9jbpru00&dl=1"
    try:
        response = requests.get(cloud_url)
        return pd.read_parquet(BytesIO(response.content))
    except:
        return pd.DataFrame()

raw_df = load_cloud_data()

@st.cache_data
def get_rfm_data(_df):
    # USE THE LOCAL CLASS DEFINED ABOVE
    analyzer = CloudCustomerAnalytics(_df) 
    return analyzer.generate_rfm()

if not raw_df.empty:
    with st.spinner("Analyzing 1M+ rows..."):
        rfm_df = get_rfm_data(raw_df)
    
    create_global_sidebar(raw_df)
    st.title("🎯 Customer Intelligence Lab")
    
    # --- DONUT CHART ---
    segment_counts = rfm_df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    fig = px.pie(segment_counts, values='Count', names='Segment', hole=0.5, 
                 color_discrete_sequence=px.colors.diverging.RdYlGn[::-1])
    st.plotly_chart(fig, use_container_width=True)

    # --- TABLES ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚠️ At Risk")
        st.dataframe(rfm_df[rfm_df['Segment'] == 'At Risk'].head(10))
    with c2:
        st.subheader("🏆 Champions")
        st.dataframe(rfm_df[rfm_df['Segment'] == 'Champions'].head(10))
else:
    st.warning("Data load failed.")