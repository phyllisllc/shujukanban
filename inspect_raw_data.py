import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')
    print(f"Columns: {df.columns.tolist()}")
    
    print("\nUnique values in '咨询结果':")
    print(df['咨询结果'].unique())
    
    print("\nUnique values in '状态':")
    print(df['状态'].unique())
    
    print("\nSample records where 咨询结果 is '成交' (if any):")
    print(df[df['咨询结果'] == '成交'].head(2))
    
    print("\nSample records where 咨询结果 is '未成交' (if any):")
    print(df[df['咨询结果'] == '未成交'].head(2))

except Exception as e:
    print(f"Error: {e}")
