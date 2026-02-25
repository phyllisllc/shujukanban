import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')
    df = df[df['咨询结果'] != '咨询结果']
    
    # Check for transactions in '非询单'
    non_inquiry_transactions = df[(df['状态'] == '非询单') & (df['咨询结果'] == '成交')]
    print("Non-inquiry transactions:")
    print(non_inquiry_transactions[['客服昵称', '状态', '咨询结果']])
    
except Exception as e:
    print(f"Error: {e}")
