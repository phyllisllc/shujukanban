import os
import pandas as pd
import sqlite3
from flask import Flask, render_template, jsonify, request, send_file
import io

app = Flask(__name__)
DB_NAME = 'sales_data.db'
EXCEL_PATH = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'

def init_db():
    try:
        if not os.path.exists(EXCEL_PATH):
            print(f"Error: Excel file not found at {EXCEL_PATH}")
            return

        # Read Excel
        print("Loading Excel data...")
        df = pd.read_excel(EXCEL_PATH, sheet_name='咨询明细-数据源')
        
        # Clean Data
        # Remove header rows where '咨询结果' == '咨询结果'
        df = df[df['咨询结果'] != '咨询结果']
        
        # Rename columns for easier SQL access
        # Columns based on analysis: ['年', '月份', '店铺', '类目', '成交金额', '日期', '顾客昵称', '商品编 号', '商品名称', '客服昵称', '状态', '咨询结果', ...]
        column_map = {
            '年': 'year',
            '月份': 'month_str',
            '店铺': 'shop',
            '类目': 'category',
            '成交金额': 'amount',
            '日期': 'date',
            '顾客昵称': 'customer',
            '商品编 号': 'sku',
            '商品名称': 'product_name',
            '客服昵称': 'sales_person',
            '状态': 'status',
            '咨询结果': 'result'
        }
        df.rename(columns=column_map, inplace=True)
        
        # Parse Month to Sortable format (YYYY-MM)
        # Assuming format '2025年6月'
        def parse_month(m_str):
            try:
                if not isinstance(m_str, str): return m_str
                # Handle cases like '2025年6月'
                if '年' in m_str and '月' in m_str:
                    year = m_str.split('年')[0]
                    month = m_str.split('年')[1].replace('月', '')
                    return f"{year}-{int(month):02d}"
                return m_str
            except:
                return m_str
        
        df['month_sortable'] = df['month_str'].apply(parse_month)
        
        # Connect to SQLite and Replace Table
        conn = sqlite3.connect(DB_NAME)
        df.to_sql('sales', conn, if_exists='replace', index=False)
        conn.close()
        print("Database initialized successfully with {} records.".format(len(df)))
        
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/options')
def get_options():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get Unique Sales Persons
        cursor.execute("SELECT DISTINCT sales_person FROM sales WHERE sales_person IS NOT NULL ORDER BY sales_person")
        persons = [row['sales_person'] for row in cursor.fetchall()]
        
        # Get Unique Months (for filtering)
        cursor.execute("SELECT DISTINCT month_sortable FROM sales WHERE month_sortable IS NOT NULL ORDER BY month_sortable DESC")
        months = [row['month_sortable'] for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({'persons': persons, 'months': months})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        person = request.args.get('person')
        month = request.args.get('month') # YYYY-MM
        
        conn = sqlite3.connect(DB_NAME)
        # No row_factory needed for pandas
        
        query = "SELECT * FROM sales WHERE 1=1"
        params = []
        
        if person and person != 'all':
            query += " AND sales_person = ?"
            params.append(person)
            
        if month and month != 'all':
            query += " AND month_sortable = ?"
            params.append(month)
            
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Calculate Metrics
        # Inquiries: status == '询单'
        inquiries = df[df['status'] == '询单'].shape[0]
        
        # Transactions: result == '成交'
        transactions = df[df['result'] == '成交'].shape[0]
        
        # Conversion Rate
        conversion_rate = 0
        if inquiries > 0:
            conversion_rate = (transactions / inquiries) * 100
        
        # Prepare Data for Charts
        chart_data = {}
        
        if not person or person == 'all':
            # Group by Sales Person
            # Filter only necessary columns to avoid type issues
            grouped = df.groupby('sales_person').agg(
                inquiries=('status', lambda x: (x == '询单').sum()),
                transactions=('result', lambda x: (x == '成交').sum())
            ).reset_index()
            
            grouped['conversion_rate'] = grouped.apply(lambda row: (row['transactions'] / row['inquiries'] * 100) if row['inquiries'] > 0 else 0, axis=1)
            
            # Sort by Inquiries desc for chart
            grouped = grouped.sort_values('inquiries', ascending=False)
            
            chart_data['labels'] = grouped['sales_person'].tolist()
            chart_data['inquiries'] = grouped['inquiries'].tolist()
            chart_data['transactions'] = grouped['transactions'].tolist()
            chart_data['conversion_rate'] = grouped['conversion_rate'].round(2).tolist()
            
        else:
            # If single person, Group by Month
            grouped = df.groupby('month_sortable').agg(
                inquiries=('status', lambda x: (x == '询单').sum()),
                transactions=('result', lambda x: (x == '成交').sum())
            ).reset_index()
            
            grouped['conversion_rate'] = grouped.apply(lambda row: (row['transactions'] / row['inquiries'] * 100) if row['inquiries'] > 0 else 0, axis=1)
            
            # Sort by Month
            grouped = grouped.sort_values('month_sortable')

            chart_data['labels'] = grouped['month_sortable'].tolist()
            chart_data['inquiries'] = grouped['inquiries'].tolist()
            chart_data['transactions'] = grouped['transactions'].tolist()
            chart_data['conversion_rate'] = grouped['conversion_rate'].round(2).tolist()

        return jsonify({
            'summary': {
                'total_inquiries': int(inquiries),
                'total_transactions': int(transactions),
                'avg_conversion_rate': round(conversion_rate, 2)
            },
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_data():
    try:
        person = request.args.get('person')
        month = request.args.get('month')
        
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT * FROM sales WHERE 1=1"
        params = []
        
        if person and person != 'all':
            query += " AND sales_person = ?"
            params.append(person)
        if month and month != 'all':
            query += " AND month_sortable = ?"
            params.append(month)
            
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered Data')
        output.seek(0)
        
        return send_file(output, download_name="sales_data_export.xlsx", as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
