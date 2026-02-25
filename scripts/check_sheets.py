import pandas as pd
import xlrd

def check_sheets(file_path):
    print(f"\n--- Sheets in: {file_path} ---")
    try:
        book = xlrd.open_workbook(file_path, on_demand=True)
        print(f"Sheet names: {book.sheet_names()}")
    except Exception as e:
        print(f"Error checking sheets: {e}")

check_sheets("data/raw/2025_Q4.xls")
check_sheets("data/raw/2023_Q1.xls")
