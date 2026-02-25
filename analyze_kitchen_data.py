import pandas as pd

file_path = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
df = pd.read_excel(file_path, sheet_name='咨询明细-数据源')

# Clean column names
df.columns = [c.strip() for c in df.columns]

# Data Cleaning
df = df[df['客服昵称'] != '客服昵 称'] # Remove header rows if any matches original header
df = df[df['客服昵称'] != '客服昵称']
df = df[df['状态'] != '状态']
df = df.dropna(subset=['店铺', '客服昵称'])
df = df[df['年'] != '-']

print(f"Total Records (Cleaned): {len(df)}")

sales_people = df['客服昵称'].unique()
print(f"Number of Sales People: {len(sales_people)}")
print(f"Sales People: {', '.join([str(x) for x in sales_people])}")

shops = df['店铺'].unique()
print(f"Shops: {', '.join([str(x) for x in shops])}")

statuses = df['状态'].unique()
print(f"Status Types: {', '.join([str(x) for x in statuses])}")

results = df['咨询结果'].unique()
print(f"Consultation Results: {', '.join([str(x) for x in results])}")

print("-" * 20)

# Function to calculate stats
def calculate_stats(group):
    inquiries = group[group['状态'] == '询单'].shape[0]
    deals = group[(group['状态'] == '询单') & (group['咨询结果'] == '成交')].shape[0]
    conversion_rate = deals / inquiries if inquiries > 0 else 0
    return pd.Series({'询单数': inquiries, '成交数': deals, '转化率': conversion_rate})

# 2. Per Sales Person Stats
sales_stats = df.groupby('客服昵称').apply(calculate_stats).sort_values('转化率', ascending=False)
print("\n--- Sales Person Stats ---")
print(sales_stats)

# 3 & 4. High/Low Performers
print("\n--- Top 3 Sales People by Conversion Rate ---")
print(sales_stats.head(3))
print("\n--- Bottom 3 Sales People by Conversion Rate ---")
print(sales_stats.tail(3))

print("\n--- Top 3 Sales People by Inquiries ---")
print(sales_stats.sort_values('询单数', ascending=False).head(3))
print("\n--- Bottom 3 Sales People by Inquiries ---")
print(sales_stats.sort_values('询单数', ascending=False).tail(3))


# 5. Correlation
correlation = sales_stats.corr()
print("\n--- Correlation ---")
print(correlation)

# 6. Yearly Comparison
year_stats = df.groupby('年').apply(calculate_stats)
print("\n--- Yearly Stats ---")
print(year_stats)

# 7. Per Shop Stats
shop_stats = df.groupby('店铺').apply(calculate_stats).sort_values('转化率', ascending=False)
print("\n--- Shop Stats ---")
print(shop_stats)
