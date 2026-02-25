import os
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_file
from sqlalchemy import create_engine, text
import io

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# EXCEL_PATH = r'G:\Trae\数据看板\Excel\智慧厨房转化率.xlsx'
EXCEL_PATH = os.path.join(BASE_DIR, 'data', '智慧厨房转化率.xlsx')
DB_PATH = os.path.join(BASE_DIR, 'dashboard.db')
DB_URI = f'sqlite:///{DB_PATH}'

engine = create_engine(DB_URI)

def init_db():
    """Initialize database and import data from Excel."""
    print("Initializing database...")
    try:
        # Read Excel
        df = pd.read_excel(EXCEL_PATH, sheet_name='咨询明细-数据源')
        
        # Clean Data
        df.columns = [c.strip() for c in df.columns]
        
        # Filter valid rows like in the analysis script
        df = df[df['客服昵称'] != '客服昵 称']
        df = df[df['客服昵称'] != '客服昵称']
        df = df[df['状态'] != '状态']
        df = df.dropna(subset=['店铺', '客服昵称'])
        df = df[df['年'] != '-']
        
        # Rename columns for database friendly names
        df = df.rename(columns={
            '年': 'year',
            '月份': 'month',
            '店铺': 'shop',
            '类目': 'category',
            '成交金额': 'amount',
            '日期': 'date',
            '顾客昵称': 'customer',
            '商品编号': 'product_id',
            '商品名称': 'product_name',
            '客服昵称': 'sales_rep',
            '状态': 'status',
            '咨询结果': 'result'
        })
        
        # Ensure date is datetime
        # df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # Keeping date as string or whatever format it is in Excel for now, 
        # but for filtering we might need to standardize. 
        # Let's inspect the date format. It seems to be mixed or just strings in some cases?
        # Based on previous analysis, there is a '日期' column.
        # Let's try to convert to datetime for better filtering
        df['date_obj'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Save to SQLite
        df.to_sql('consultations', engine, if_exists='replace', index=False)
        print("Data imported successfully.")
        
    except Exception as e:
        print(f"Error importing data: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/options')
def get_options():
    """Get filter options."""
    try:
        with engine.connect() as conn:
            shops = pd.read_sql("SELECT DISTINCT shop FROM consultations WHERE shop IS NOT NULL ORDER BY shop", conn)['shop'].tolist()
            sales_reps = pd.read_sql("SELECT DISTINCT sales_rep FROM consultations WHERE sales_rep IS NOT NULL ORDER BY sales_rep", conn)['sales_rep'].tolist()
        return jsonify({'shops': shops, 'sales_reps': sales_reps})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics and chart data."""
    try:
        # Get filters
        shop = request.args.get('shop')
        sales_rep = request.args.get('sales_rep')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = "SELECT * FROM consultations WHERE 1=1"
        params = {}
        
        if shop:
            query += " AND shop = :shop"
            params['shop'] = shop
        if sales_rep:
            query += " AND sales_rep = :sales_rep"
            params['sales_rep'] = sales_rep
        if start_date:
            query += " AND date_obj >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND date_obj <= :end_date"
            params['end_date'] = end_date
            
        df = pd.read_sql(query, engine, params=params)
        
        if df.empty:
             return jsonify({
                'cards': {'inquiries': 0, 'deals': 0, 'conversion_rate': 0, 'shop_count': 0},
                'charts': {}
            })

        # --- Cards ---
        inquiries = df[df['status'] == '询单'].shape[0]
        deals = df[(df['status'] == '询单') & (df['result'] == '成交')].shape[0]
        conversion_rate = (deals / inquiries * 100) if inquiries > 0 else 0
        shop_count = df['shop'].nunique()
        
        cards = {
            'inquiries': int(inquiries),
            'deals': int(deals),
            'conversion_rate': round(conversion_rate, 2),
            'shop_count': int(shop_count)
        }
        
        # --- Charts Data Helper ---
        def get_group_stats(group_col):
            stats = df.groupby(group_col).apply(lambda x: pd.Series({
                'inquiries': x[x['status'] == '询单'].shape[0],
                'deals': x[(x['status'] == '询单') & (x['result'] == '成交')].shape[0]
            })).reset_index()
            
            stats['conversion_rate'] = stats.apply(lambda row: (row['deals'] / row['inquiries'] * 100) if row['inquiries'] > 0 else 0, axis=1)
            return stats

        # Sales Rep Stats
        sales_stats = get_group_stats('sales_rep')
        
        # Shop Stats
        shop_stats = get_group_stats('shop')
        
        # Prepare Chart Data (Top 10 for readability)
        def format_chart_data(data, label_col, value_col, sort_by=None):
            if sort_by:
                data = data.sort_values(sort_by, ascending=False)
            
            return {
                'labels': data[label_col].tolist(),
                'values': data[value_col].tolist()
            }

        charts = {
            'sales_inquiries': format_chart_data(sales_stats, 'sales_rep', 'inquiries', 'inquiries'),
            'sales_deals': format_chart_data(sales_stats, 'sales_rep', 'deals', 'deals'),
            'sales_conversion': format_chart_data(sales_stats, 'sales_rep', 'conversion_rate', 'conversion_rate'),
            
            'shop_inquiries': format_chart_data(shop_stats, 'shop', 'inquiries', 'inquiries'),
            'shop_deals': format_chart_data(shop_stats, 'shop', 'deals', 'deals'),
            'shop_conversion': format_chart_data(shop_stats, 'shop', 'conversion_rate', 'conversion_rate'),
        }
        
        return jsonify({'cards': cards, 'charts': charts})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_data():
    """Export filtered data to Excel."""
    try:
        # Get filters (same as stats)
        shop = request.args.get('shop')
        sales_rep = request.args.get('sales_rep')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = "SELECT * FROM consultations WHERE 1=1"
        params = {}
        
        if shop:
            query += " AND shop = :shop"
            params['shop'] = shop
        if sales_rep:
            query += " AND sales_rep = :sales_rep"
            params['sales_rep'] = sales_rep
        if start_date:
            query += " AND date_obj >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND date_obj <= :end_date"
            params['end_date'] = end_date
            
        df = pd.read_sql(query, engine, params=params)
        
        # Drop helper column
        if 'date_obj' in df.columns:
            df = df.drop(columns=['date_obj'])
            
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered Data')
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='export_data.xlsx'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize DB on start
    init_db()
    # Use 0.0.0.0 to allow access from other devices on the same network
    app.run(host='0.0.0.0', port=5001, debug=True)
