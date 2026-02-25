import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')
    print("Columns:", df.columns.tolist())
    print("First 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading Excel file: {e}")
