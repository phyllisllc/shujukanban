import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')
    
    # Filter out header rows
    df = df[df['咨询结果'] != '咨询结果']
    
    print("Cross tabulation of '状态' and '咨询结果':")
    print(pd.crosstab(df['状态'], df['咨询结果']))
    
except Exception as e:
    print(f"Error: {e}")
