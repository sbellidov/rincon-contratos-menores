import pandas as pd
import xlrd
import os

raw_dir = 'data/raw'
files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.xls') or f.endswith('.xlsx')])

for filename in files:
    file_path = os.path.join(raw_dir, filename)
    print(f"\n--- Analyzing {filename} ---")
    try:
        book = xlrd.open_workbook(file_path, on_demand=True)
        sheet_names = book.sheet_names()
        print(f"Sheets: {sheet_names}")
        
        for sheet_name in sheet_names:
            if 'AYTO' in sheet_name.upper() or 'DEP' in sheet_name.upper() or 'CONTRATO' in sheet_name.upper():
                print(f"  Inspecting sheet: {sheet_name}")
                # Read first 10 rows without assuming header to find where it starts
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=10)
                for i, row in df.iterrows():
                    # Look for a row that contains typical headers like 'OBJETO' or 'ADJUDICATARIO'
                    row_str = " | ".join([str(val) for val in row.values])
                    print(f"    Row {i}: {row_str[:150]}...")
                    if 'OBJETO' in row_str.upper() or 'ADJUDICATARIO' in row_str.upper():
                        print(f"    ==> POSSIBLE HEADER FOUND AT ROW {i}")
    except Exception as e:
        print(f"Error: {e}")

