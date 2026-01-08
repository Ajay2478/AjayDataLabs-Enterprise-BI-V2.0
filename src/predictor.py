import pandas as pd
import numpy as np
import os
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

class RevenuePredictor:
    def __init__(self):
        self.input_path = os.getenv("PROCESSED_DATA_PATH")
        self.model_save_path = "src/models/revenue_model.pkl"

    def train_forecaster(self):
        print("🚀 Training Advanced XGBoost Revenue Engine...")
        df = pd.read_parquet(self.input_path)
        
        # 1. Monthly Resampling
        monthly_df = df.set_index('InvoiceDate')['Line_Total'].resample('MS').sum().reset_index()
        
        # 2. FEATURE ENGINEERING (The 'Beyond' Part)
        monthly_df['Month_Ordinal'] = np.arange(len(monthly_df))
        # Lag Features: Teaching the model about its own history
        monthly_df['Lag_1'] = monthly_df['Line_Total'].shift(1)
        monthly_df['Lag_2'] = monthly_df['Line_Total'].shift(2)
        
        # Rolling Mean: Capturing the general 'momentum'
        monthly_df['Rolling_Mean'] = monthly_df['Line_Total'].shift(1).rolling(window=3).mean()
        
        # Drop rows with NaN caused by shifting
        monthly_df = monthly_df.dropna()
        
        # 3. Defining Features and Target
        features = ['Month_Ordinal', 'Lag_1', 'Lag_2', 'Rolling_Mean']
        X = monthly_df[features]
        y = monthly_df['Line_Total']

        # 4. Split (Shuffle=False is CRITICAL for Time Series)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # 5. XGBoost Implementation
        # We use objective='reg:squarederror' for regression tasks
        model = xgb.XGBRegressor(
            n_estimators=500, 
            learning_rate=0.01, 
            max_depth=6, 
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror'
        )
        
        model.fit(X_train, y_train)

        # 6. Save the Brain
        os.makedirs("src/models", exist_ok=True)
        joblib.dump(model, self.model_save_path)
        
        # Performance Check
        score = model.score(X_test, y_test)
        print(f"✅ XGBoost Model Saved. R² Score: {score:.4f}")
        
        return model

if __name__ == "__main__":
    predictor = RevenuePredictor()
    predictor.train_forecaster()