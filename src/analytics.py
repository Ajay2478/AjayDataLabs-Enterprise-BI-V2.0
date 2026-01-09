import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

class CustomerAnalytics:
    def __init__(self, df=None):
        # The Senior Fix: Explicitly check if the object is a DataFrame
        if isinstance(df, pd.DataFrame):
            self.df = df
        else:
            # Fallback for local dev/testing
            path = os.getenv("PROCESSED_DATA_PATH")
            if path and os.path.exists(path):
                self.df = pd.read_parquet(path)
            else:
                self.df = pd.DataFrame() # Avoid NoneType errors
            
    def generate_rfm(self):
        if self.df.empty:
            return pd.DataFrame()

        # USE THE INTERNAL STATE
        df = self.df
        
        snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
        
        rfm = df.groupby('Customer ID').agg({
            'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
            'Invoice': 'nunique',
            'Line_Total': 'sum'
        }).rename(columns={
            'InvoiceDate': 'Recency',
            'Invoice': 'Frequency',
            'Line_Total': 'Monetary'
        })

        rfm = rfm[rfm.index.notnull()]

        # Standard Scoring
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str)
        
        segs = {
            r'[1-2][1-2]': 'Hibernating',
            r'[1-2][3-4]': 'At Risk',
            r'[1-2]5': 'Can\'t Lose Them',
            r'3[1-2]': 'About to Sleep',
            r'33': 'Need Attention',
            r'[3-4][4-5]': 'Loyalists',
            r'41': 'Promising',
            r'51': 'New Customers',
            r'[4-5][2-3]': 'Potential Loyalists',
            r'5[4-5]': 'Champions'
        }
        rfm['Segment'] = rfm['RFM_Score'].replace(segs, regex=True)
        return rfm

if __name__ == "__main__":
    # Test block for local development
    analyzer = CustomerAnalytics()
    if not analyzer.df.empty:
        rfm_results = analyzer.generate_rfm()
        print(rfm_results['Segment'].value_counts())