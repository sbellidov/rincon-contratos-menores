import pandas as pd
import os

def inspect_excel(file_path):
    print(f"\n--- Inspecting: {file_path} ---")
    try:
        engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
        
        # Try to read with row 1 as header (common in these documents)
        df = pd.read_excel(file_path, engine=engine, header=1)
        print(f"Refined Columns: {df.columns.tolist()}")
        print(f"Sample data (row 0):\n{df.iloc[0].to_dict()}")
        print(f"Total rows: {len(df)}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

raw_data_dir = 'data/raw'
for filename in os.listdir(raw_data_dir):
    if filename.endswith('.xls') or filename.endswith('.xlsx'):
        inspect_excel(os.path.join(raw_data_dir, filename))
