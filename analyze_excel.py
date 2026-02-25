import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path)
    print("Head of the dataframe:")
    print(df.head())
    print("\nInfo:")
    print(df.info())
    
    # 1. Total records and sales personnel
    total_records = len(df)
    unique_sales_personnel = df['销售员'].nunique()
    print(f"\n1. Total records: {total_records}")
    print(f"Unique sales personnel: {unique_sales_personnel}")
    print(f"Sales personnel list: {df['销售员'].unique()}")

    # 2. Inquiries, Transactions, Conversion Rates
    # Assuming columns are named '询单', '成交', '转化率' or similar. 
    # Based on the head output, I will adjust if needed.
    
except Exception as e:
    print(f"Error reading excel file: {e}")
