import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os
import sys
from dotenv import load_dotenv

# 1. PATHING & ENVIRONMENT (Critical for finding 'src')
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# Now we can safely import your shared components
from src.ui_components import create_global_sidebar

# 2. PAGE CONFIG
st.set_page_config(page_title="Predictor Lab", layout="wide")

# 3. ADVANCED FEATURE ENGINEERING (The 'Beyond' Logic)
@st.cache_data
def get_engineered_data():
    path = os.getenv("PROCESSED_DATA_PATH")
    if not path or not os.path.exists(path):
        return pd.DataFrame()

    df_raw = pd.read_parquet(path)
    
    # Monthly Resampling
    monthly = df_raw.set_index('InvoiceDate')['Line_Total'].resample('MS').sum().reset_index()
    
    # Feature Engineering (Must match training exactly)
    monthly['Month_Ordinal'] = np.arange(len(monthly))
    monthly['Lag_1'] = monthly['Line_Total'].shift(1)
    monthly['Lag_2'] = monthly['Line_Total'].shift(2)
    monthly['Rolling_Mean'] = monthly['Line_Total'].shift(1).rolling(window=3).mean()
    
    return monthly.dropna(), df_raw

# 4. LOAD DATA & PERSISTENT SIDEBAR
# We need monthly_df for the chart and raw_df for the sidebar filters
monthly_df, raw_df = get_engineered_data()

# Restoration of the persistent V1 Sidebar
date_range = create_global_sidebar(raw_df)

# 5. PAGE CONTENT
st.title("🔮 Predictive Revenue Lab (XGBoost Edition)")
st.markdown("---")

model_path = "src/models/revenue_model.pkl"

if not monthly_df.empty and os.path.exists(model_path):
    # 6. Load the trained XGBoost Brain
    model = joblib.load(model_path)
    
    # 7. Sidebar - Strategy Simulator
    st.sidebar.markdown("---")
    st.sidebar.header("🕹️ Strategy Simulator")
    st.sidebar.info("Simulate revenue growth based on marketing lift.")
    lift = st.sidebar.slider("Simulated Marketing Lift (%)", 0, 50, 0) / 100

    # 8. Generate Predictions
    features = ['Month_Ordinal', 'Lag_1', 'Lag_2', 'Rolling_Mean']
    current_preds = model.predict(monthly_df[features])
    
    # Apply lift for simulation
    simulated_preds = current_preds * (1 + lift)

    # 9. Visualization
    fig = go.Figure()

    # Actual Revenue Data
    fig.add_trace(go.Scatter(
        x=monthly_df['InvoiceDate'], y=monthly_df['Line_Total'], 
        name="Actual Revenue", line=dict(color='royalblue', width=3)
    ))

    # XGBoost Baseline
    fig.add_trace(go.Scatter(
        x=monthly_df['InvoiceDate'], y=current_preds, 
        name="Model Baseline", line=dict(color='white', dash='dot', width=1)
    ))

    # Simulated Strategy Line
    fig.add_trace(go.Scatter(
        x=monthly_df['InvoiceDate'], y=simulated_preds, 
        name="Simulated Strategy", line=dict(color='#00FFCC', width=4)
    ))

    fig.update_layout(
        title="Revenue Velocity: Strategic Impact Simulation",
        xaxis_title="Timeline", yaxis_title="Revenue ($)",
        template="plotly_dark", hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 10. Senior Metrics
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Model Baseline (Last Month)", f"${current_preds[-1]/1e3:.1f}k")
    with c2:
        st.metric("Simulated Target", f"${simulated_preds[-1]/1e3:.1f}k", delta=f"{lift*100:.0f}% Lift")

else:
    st.warning("⚠️ Prerequisites missing. Ensure you have run data_loader.py and predictor.py.")