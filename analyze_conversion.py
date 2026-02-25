import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
try:
    # Load raw data
    df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')
    
    # Filter out header rows (where '咨询结果' column has value '咨询结果')
    df = df[df['咨询结果'] != '咨询结果']
    
    # 1. Basic Stats
    total_records = len(df)
    unique_sales_personnel = df['客服昵称'].nunique()
    sales_personnel_list = df['客服昵称'].unique()
    
    print(f"Total records: {total_records}")
    print(f"Number of sales personnel: {unique_sales_personnel}")
    print(f"Sales personnel: {', '.join(map(str, sales_personnel_list))}")
    
    # 2. Metrics per Sales Person
    # Group by '客服昵称'
    # Inquiries: Count where '状态' == '询单'
    # Transactions: Count where '咨询结果' == '成交'
    
    # Create helper columns
    df['is_inquiry'] = (df['状态'] == '询单').astype(int)
    df['is_transaction'] = (df['咨询结果'] == '成交').astype(int)
    
    # Groupby
    stats = df.groupby('客服昵称').agg(
        inquiries=('is_inquiry', 'sum'),
        transactions=('is_transaction', 'sum')
    ).reset_index()
    
    # Calculate Conversion Rate
    stats['conversion_rate'] = stats['transactions'] / stats['inquiries']
    # Handle division by zero
    stats['conversion_rate'] = stats['conversion_rate'].fillna(0)
    
    # Sort by Conversion Rate descending
    stats_sorted = stats.sort_values(by='conversion_rate', ascending=False)
    
    print("\n--- Sales Personnel Performance ---")
    print(stats_sorted.to_string(index=False, formatters={'conversion_rate': '{:.2%}'.format}))
    
    # 3. High/Low Performers
    # Define thresholds or just top/bottom
    print("\n--- Top 3 Performers (by Conversion Rate) ---")
    print(stats_sorted.head(3).to_string(index=False, formatters={'conversion_rate': '{:.2%}'.format}))
    
    print("\n--- Bottom 3 Performers (by Conversion Rate) ---")
    # Filter out those with 0 inquiries if desired, but here we show all
    print(stats_sorted.tail(3).to_string(index=False, formatters={'conversion_rate': '{:.2%}'.format}))
    
    print("\n--- Top 3 Performers (by Transactions) ---")
    print(stats.sort_values(by='transactions', ascending=False).head(3).to_string(index=False, formatters={'conversion_rate': '{:.2%}'.format}))

    print("\n--- Top 3 Performers (by Inquiries) ---")
    print(stats.sort_values(by='inquiries', ascending=False).head(3).to_string(index=False, formatters={'conversion_rate': '{:.2%}'.format}))

    # 4. Relationship Analysis
    correlation = stats[['inquiries', 'transactions', 'conversion_rate']].corr()
    print("\n--- Correlation Matrix ---")
    print(correlation)
    
    # Additional Insight: Average Conversion Rate
    avg_conversion_rate = stats['transactions'].sum() / stats['inquiries'].sum()
    print(f"\nOverall Conversion Rate: {avg_conversion_rate:.2%}")

except Exception as e:
    print(f"Error: {e}")
