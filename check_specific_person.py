import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')
    df = df[df['咨询结果'] != '咨询结果']
    
    person = '罗广强'
    print(f"Data for {person}:")
    print(df[df['客服昵称'] == person][['状态', '咨询结果']])
    
    person2 = '林静宜'
    print(f"\nData for {person2}:")
    print(df[df['客服昵称'] == person2][['状态', '咨询结果']])

except Exception as e:
    print(f"Error: {e}")
