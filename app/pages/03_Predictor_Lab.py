import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os
import sys
import requests
from io import BytesIO
from dotenv import load_dotenv

# 1. PATHING & ENVIRONMENT (Critical for Cloud compatibility)
load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import your shared components
from src.ui_components import create_global_sidebar

# 2. PAGE CONFIG
st.set_page_config(page_title="Predictor Lab", layout="wide")

# 3. CLOUD-AWARE DATA ENGINE
@st.cache_data
def load_production_data():
    """
    Handles million-row data streaming for the prediction engine.
    """
    local_path = os.getenv("PROCESSED_DATA_PATH")
    if local_path and os.path.exists(local_path):
        return pd.read_parquet(local_path)
    
    # Cloud Stream from your verified Dropbox link
    cloud_url = "https://www.dropbox.com/scl/fi/5daz0xt5dthm24hbyioxb/cleaned_data.parquet?rlkey=wvkn08glbo3ofur47l77fy978&st=9jbpru00&dl=1"
    
    try:
        response = requests.get(cloud_url)
        response.raise_for_status()
        return pd.read_parquet(BytesIO(response.content))
    except Exception as e:
        st.error(f"⚠️ Prediction Engine Data Sync Failed: {e}")
        return pd.DataFrame()

# 4. ADVANCED FEATURE ENGINEERING
@st.cache_data
def get_engineered_data(_df_raw):
    """
    Transforms raw data into time-series features for XGBoost.
    """
    if _df_raw.empty:
        return pd.DataFrame()

    # Monthly Resampling
    monthly = _df_raw.set_index('InvoiceDate')['Line_Total'].resample('MS').sum().reset_index()
    
    # Feature Engineering (Must match training features exactly)
    monthly['Month_Ordinal'] = np.arange(len(monthly))
    monthly['Lag_1'] = monthly['Line_Total'].shift(1)
    monthly['Lag_2'] = monthly['Line_Total'].shift(2)
    monthly['Rolling_Mean'] = monthly['Line_Total'].shift(1).rolling(window=3).mean()
    
    return monthly.dropna()

# 5. INITIALIZE DATA
raw_df = load_production_data()
monthly_df = get_engineered_data(raw_df)

if not raw_df.empty:
    # Persistent Sidebar Restoration
    date_range = create_global_sidebar(raw_df)

    # 6. PAGE CONTENT
    st.title("🔮 Predictive Revenue Lab (XGBoost Edition)")
    st.markdown("---")

    # Cloud-Path for Model (Ensures it works locally and on cloud)
    model_path = os.path.join(os.path.dirname(__file__), "../../src/models/revenue_model.pkl")

    if not monthly_df.empty and os.path.exists(model_path):
        # 7. Load the trained XGBoost Brain
        model = joblib.load(model_path)
        
        # 8. Sidebar - Strategy Simulator
        st.sidebar.markdown("---")
        st.sidebar.header("🕹️ Strategy Simulator")
        lift = st.sidebar.slider("Simulated Marketing Lift (%)", 0, 50, 0) / 100

        # 9. Generate Predictions
        features = ['Month_Ordinal', 'Lag_1', 'Lag_2', 'Rolling_Mean']
        current_preds = model.predict(monthly_df[features])
        simulated_preds = current_preds * (1 + lift)

        # 10. Visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_df['InvoiceDate'], y=monthly_df['Line_Total'], name="Actual Revenue", line=dict(color='royalblue', width=3)))
        fig.add_trace(go.Scatter(x=monthly_df['InvoiceDate'], y=current_preds, name="Model Baseline", line=dict(color='white', dash='dot', width=1)))
        fig.add_trace(go.Scatter(x=monthly_df['InvoiceDate'], y=simulated_preds, name="Simulated Strategy", line=dict(color='#00FFCC', width=4)))

        fig.update_layout(title="Revenue Velocity Simulation", template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
        # 11. Metrics
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Baseline Forecast", f"${current_preds[-1]/1e3:.1f}k")
        c2.metric("Target with Lift", f"${simulated_preds[-1]/1e3:.1f}k", delta=f"{lift*100:.0f}%")
    else:
        st.warning("⚠️ ML Model not found in src/models/. Ensure revenue_model.pkl is uploaded.")