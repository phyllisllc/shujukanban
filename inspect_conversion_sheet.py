import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='转化率')
    print("First 10 rows of '转化率' sheet:")
    print(df.head(10))
    
except Exception as e:
    print(f"Error: {e}")
