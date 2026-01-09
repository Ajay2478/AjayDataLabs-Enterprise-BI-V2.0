# 💎 Technical Project Report: AjayDataLabs V2.0

## 1. Executive Summary
The AjayDataLabs BI Suite is a production-ready analytics platform designed to process over 1.06M rows of retail data. The project successfully implements an end-to-end SDLC, from cloud-native data streaming to predictive modeling using XGBoost.

## 2. Data Engineering & Architecture
### Cloud Integration
To bypass GitHub storage limitations and ensure a cloud-native experience, data is served via a **Binary Stream Engine**.
- **Source:** Compressed Parquet (1.06M rows).
- **Transport:** HTTP streaming via `requests` and `io.BytesIO`.
- **Latency Management:** Implemented multi-stage caching using Streamlit's `@st.cache_data`, ensuring sub-second response times for the UI after the initial data pull.

### Modular Codebase
The project follows a modular architecture to ensure scalability:
- `src/features.py`: Centralized feature engineering factory.
- `src/analytics.py`: Class-based RFM segmentation logic.
- `src/ui_components.py`: Shared UI elements for brand consistency.

## 3. Machine Learning & Predictive Analytics
### Model Architecture
The system utilizes an **XGBoost Regressor** tuned for time-series forecasting.
- **Features:** Month Ordinal, Seasonal Month Number, Q4 Indicator, 1-2 Month Lags, 3-Month Rolling Averages, and Revenue Momentum.
- **Optimization:** Hyperparameter tuning (learning_rate=0.05, n_estimators=1000).

### Validation Strategy

To prevent **Data Leakage**, the model was validated using a blind **Out-of-Sample Test**:
- **Train-Test Split:** 80/20 chronological split (no shuffling to preserve time-series integrity).
- **Final Metrics:** Achieved high mathematical alignment on unseen test data, indicating robust generalization for the current dataset patterns.

## 4. Business Intelligence Insights
- **RFM Analysis:** Segmented the customer base into 10 distinct tiers. Identified that **25.8%** of customers are "Hibernating," suggesting a high-priority need for re-engagement marketing.
- **Geospatial Logistics:** Identified the UK as the core revenue driver while France and Germany represent the highest-velocity expansion markets based on revenue density mapping.

## 5. Conclusion
AjayDataLabs V2.0 proves that high-volume e-commerce data can be transformed into actionable strategy. The integration of a "What-If" simulator provides stakeholders with a quantitative tool to measure marketing ROI before execution.