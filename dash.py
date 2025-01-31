from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import os

app = Flask(__name__)


os.makedirs('static', exist_ok=True)
# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lionel.A.messi100',
    'database': 'lms'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def generate_monthly_revenue_graph():
    monthly_revenue = {
        'January': 52000,
        'February': 51000,
        'March': 53000,
    }
    months = list(monthly_revenue.keys())
    revenues = list(monthly_revenue.values())

    plt.figure(figsize=(8, 6))
    plt.plot(months, revenues, marker='o', linestyle='-', color='r')
    plt.title('Monthly Revenue')
    plt.xlabel('Month')
    plt.ylabel('Revenue (pkr)')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf-8')
    
    return graph_url

def generate_lease_status_pie_chart():
    lease_statuses = ['Active', 'Expired']
    lease_counts = [5, 3]

    plt.figure(figsize=(7, 7))
    plt.pie(lease_counts, labels=lease_statuses, autopct='%1.1f%%', startangle=90)
    plt.title('Lease Status Distribution')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    pie_chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    
    return pie_chart_url

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM lms_table')
    leases = cursor.fetchall()

    today = datetime.now().date()
    cursor.execute('SELECT * FROM lms_table WHERE lease_date < %s', (today,))
    pending_leases = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM lms_table')
    total_leases = cursor.fetchone()['COUNT(*)']

    cursor.execute('SELECT COUNT(*) FROM properties')
    active_properties = cursor.fetchone()['COUNT(*)']

    cursor.execute('SELECT COUNT(DISTINCT name) FROM lms_table')
    total_tenants = cursor.fetchone()['COUNT(DISTINCT name)']

    cursor.close()
    conn.close()

    graph_url = generate_monthly_revenue_graph()
    pie_chart_url = generate_lease_status_pie_chart()

    return render_template(
        'index.html', 
        leases=leases, 
        pending_leases=pending_leases,
        total_leases=total_leases,
        active_leases=active_properties,
        total_tenants=total_tenants,
        graph_url=graph_url, 
        pie_chart_url=pie_chart_url
    )

@app.route('/leases')
def view_leases():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM lms_table')
    leases = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('leases.html', leases=leases)
@app.route('/inventory')
def view_inventory():
    

    return render_template('properties.html')
@app.route('/employees')
def view_employees():
    employees="There are 2 employees working in the company."

    return render_template('employees.html', employees=employees)
@app.route('/properties')
def view_properties():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM properties")
    properties = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('properties.html', properties=properties)



@app.route('/active_leases')
def view_active_leases():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = datetime.now().date()
    cursor.execute('SELECT * FROM lms_table')
    active_leases = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('leases.html',active_leases=active_leases)

@app.route('/tenants')
def view_tenants():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT DISTINCT name, phone FROM lms_table')
    tenants = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tenants.html', tenants=tenants)
@app.route('/transactions')
def view_transactions():
    # Replace with your actual transaction query or data handling
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM transactions')  # Example table
    transactions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/add_tenant', methods=['GET', 'POST'])
def add_tenant():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        rent_amount = int(request.form['rent_amount'])
        lease_date = request.form['lease_date']
        lease_number = request.form['lease_number']
        payment_period = request.form['payment_period']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lms_table (name, phone, rent_amount, lease_date, lease_number, payment_period)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, phone, rent_amount, lease_date, lease_number, payment_period))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_tenants'))

    return render_template('add_tenant.html')
@app.route('/add_properties', methods=['GET', 'POST'])
def add_properties():
    if request.method == 'POST':
        name = request.form['tenant_name']
        property_name= request.form['property_name']
        rent_amount = int(request.form['rent_amount'])
        lease_date = request.form['lease_number']
        lease_number = request.form['location']
        

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO properties (tenant_name,property_name,rent_amount,lease_number, location)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, property_name, rent_amount, lease_date, lease_number))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_properties'))

    return render_template('add_properties.html')

@app.route('/revenue')
def view_revenue():
    monthly_revenue = 52000
    return render_template('revenue.html', monthly_revenue=monthly_revenue)

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS lms_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        rent_amount FLOAT NOT NULL,
        lease_date DATE NOT NULL,
        lease_number VARCHAR(20) UNIQUE NOT NULL,
        payment_period VARCHAR(20) NOT NULL
    )
    """
    cursor.execute(create_table_sql)
    
    cursor.execute("SELECT COUNT(*) FROM lms_table")
    count = cursor.fetchone()[0]
    
    # Insert demo data if the table is empty
    if count == 0:
        demo_data = [
            ("John Doe", "555-0101", 1200, "2023-12-15", "L2024-001", "Monthly"),
            ("Jane Smith", "555-0102", 1500, "2023-11-20", "L2024-002", "Monthly"),
            ("Mike Johnson", "555-0103", 2000, "2024-03-25", "L2024-003", "Quarterly"),
            ("Emma Brown", "555-0104", 1800, "2024-01-10", "L2024-004", "Monthly"),
            ("Tom White", "555-0105", 2500, "2024-02-05", "L2024-005", "Monthly"),
            ("Sophia Green", "555-0106", 2200, "2024-02-01", "L2024-006", "Quarterly")
        ]
        insert_sql = """INSERT INTO lms_table 
                       (name, phone, rent_amount, lease_date, lease_number, payment_period) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.executemany(insert_sql, demo_data)
        conn.commit()
    
    cursor.close()
    conn.close()
    
    app.run(debug=True)
