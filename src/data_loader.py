import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

class DataEngineer:
    def __init__(self):
        # Load .env from the root directory
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
        
        self.raw_path = os.getenv("RAW_DATA_PATH")
        self.output_path = os.getenv("PROCESSED_DATA_PATH")
        
        if not self.raw_path:
            raise FileNotFoundError("❌ RAW_DATA_PATH not found in .env file!")
        print(f"📂 Target File: {self.raw_path}")

    def clean_data(self):
        print("🚀 Starting Enterprise ETL Pipeline...")
        
        dtype_spec = {
            'Invoice': str,
            'StockCode': str,
            'Description': str,
            'Quantity': np.int32,
            'Price': np.float32,
            'Customer ID': str
        }
        
        # FIX: Ensure this is indented correctly inside the function
        df = pd.read_csv(
            self.raw_path, 
            dtype=dtype_spec, 
            parse_dates=['InvoiceDate'], 
            encoding='ISO-8859-1'
        )
        
        # FIX: Define initial_count before cleaning
        initial_count = len(df)
        
        # 1. Handle Cancellations
        df['Is_Cancelled'] = df['Invoice'].str.startswith('C', na=False)
        
        # 2. Feature Engineering
        df['Line_Total'] = df['Quantity'] * df['Price']
        
        # 3. Cleaning
        df = df.dropna(subset=['Description'])
        
        # 4. Remove obvious data errors (Price must be > 0)
        df = df[(df['Price'] > 0)]
        
        print(f"✅ Cleaned {initial_count - len(df)} outlier/junk rows.")
        print(f"📊 Final Row Count: {len(df)}")
        
        # 5. Export to Parquet (The Enterprise Way)
        # Create folder if it doesn't exist
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_parquet(self.output_path, index=False)
        
        print(f"📦 Gold Layer saved to: {self.output_path}")
        return df

if __name__ == "__main__":
    engineer = DataEngineer()
    engineer.clean_data()