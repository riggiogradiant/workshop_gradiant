from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

# Get the current directory (where app.py is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app, pointing to the current directory for templates
app = Flask(__name__, template_folder=current_dir)
app.secret_key = 'your-secret-key-here'

# Create separate databases
def create_users_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT, 
                    password TEXT, 
                    role TEXT)''')

    # Insert Fake Users with roles
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'password123', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('superadmin', 'supersecret', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('manager1', 'managerpass', 'manager')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('user1', 'userpass1', 'user')")
    
    conn.commit()
    conn.close()


def create_customers_db():
    conn = sqlite3.connect('customers.db')  # Use the same database file
    c = conn.cursor()

    # Create the customers table with user_id to link each customer to a specific user
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            address TEXT,
            phone TEXT,
            order_details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Insert sample customer order data with user_id corresponding to a user
    c.executemany('''
        INSERT INTO customers (user_id, name, email, address, phone, order_details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (1, 'Alice Johnson', 'alice@example.com', '123 Main St, New York', '555-1234', 'Order: iPhone 15'),
        (2, 'Bob Smith', 'bob@example.com', '456 Oak Ave, Los Angeles', '555-5678', 'Order: MacBook Pro'),
        (3, 'Charlie Davis', 'charlie@example.com', '789 Pine Rd, Chicago', '555-9876', 'Order: PlayStation 5'),
        (4, 'David White', 'david@example.com', '321 Maple St, Houston', '555-4321', 'Order: Xbox Series X'),
        (5, 'Emma Brown', 'emma@example.com', '654 Cedar Ln, Miami', '555-2468', 'Order: Samsung Galaxy S24')
    ])

    conn.commit()
    conn.close()


# Vulnerable login check (SQL Injection vulnerable)
def check_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # 🚨 SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    c.execute(query)

    result = c.fetchone()
    conn.close()
    return result


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST']) # ' OR 1=1 --
def login():
    username = request.form['username']
    password = request.form['password']

    user = check_login(username, password)
    if user:
        session['user_id'] = user[0]  # Store the user's ID in the session
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('failed'))

@app.route('/search')
def search():
    search_query = request.args.get('query', '')

    # Get the logged-in user's ID from session
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('failed'))  # Redirect to failed page if no user is logged in

    conn = sqlite3.connect('customers.db')
    c = conn.cursor()

    # Making the query vulnerable to SQL injection by using string concatenation
    query = f"SELECT * FROM customers WHERE user_id = {user_id} AND name LIKE '%{search_query}%'" # ' OR '1'='1' --

    # Log the query being executed (for debugging)
    print(f"Executing query: {query}")  # Debugging purpose
    
    c.execute(query)  # This is where the SQL injection happens
    results = c.fetchall()
    conn.close()

    return render_template('search.html', customers=results)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/failed')
def failed():
    return render_template('failed.html')

if __name__ == '__main__':
    create_users_db()  # Ensure the database and sample user exist
    create_customers_db()  # Ensure the customers database and table exist (fix this line to call the function)
    app.run(debug=True)
