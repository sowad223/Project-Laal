from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management


# Database setup function
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create donations table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create volunteers table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        skills TEXT,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create admin table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    ''')

    # Create tasks table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER,
        task TEXT NOT NULL,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (volunteer_id) REFERENCES volunteers (id)
    )
    ''')

    # Insert default admin if it doesn't exist
    cursor.execute('SELECT * FROM admin WHERE username = ?', ('sowadrahman',))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)',
                       ('sowadrahman', 'projectlaal'))

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('first_page.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/project')
def project():
    return render_template('project.html')


@app.route('/issue')
def issue():
    return render_template('issue.html')


@app.route('/new')
def new():
    return render_template('new.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        phone = request.form.get('Phone')
        address = request.form.get('Address')
        payment_method = request.form.get('Payment Method')

        # Insert the data into the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO donations (name, email, phone, address, payment_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, address, payment_method))
        conn.commit()
        conn.close()

        return redirect('/')  # Redirect to home after submission

    return render_template('donate.html')  # Render donation form on GET request


@app.route('/volunteer_signup', methods=['GET', 'POST'])
def volunteer_signup():
    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        phone = request.form.get('Phone')
        skills = request.form.get('Skills')
        password = request.form.get('Password')

        # Insert the volunteer into the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO volunteers (name, email, phone, skills, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, skills, password))
        conn.commit()
        conn.close()

        flash('Volunteer signed up successfully!', 'success')
        return redirect('/')  # Redirect to home after signup

    return render_template('volunteer_signup.html')


@app.route('/volunteer_login', methods=['GET', 'POST'])
def volunteer_login():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        # Check if the volunteer exists with the provided password
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM volunteers WHERE email = ? AND password = ?', (email, password))
        volunteer = cursor.fetchone()
        conn.close()

        if volunteer:
            session['volunteer_id'] = volunteer[0]  # Store volunteer ID in session
            flash('Logged in successfully!', 'success')
            return redirect('/volunteer_dashboard')  # Redirect to volunteer dashboard
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('volunteer_login.html')


@app.route('/volunteer_dashboard')
def volunteer_dashboard():
    if 'volunteer_id' not in session:
        return redirect('/volunteer_login')

    volunteer_id = session['volunteer_id']

    # Fetch assigned tasks for the logged-in volunteer
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE volunteer_id = ?', (volunteer_id,))
    tasks = cursor.fetchall()
    conn.close()

    return render_template('volunteer_dashboard.html', tasks=tasks)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin_username'] = username
            flash('Logged in successfully!', 'success')
            return redirect('/admin_dashboard')  # Redirect to admin dashboard after login
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_username' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM volunteers')
    volunteers = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', volunteers=volunteers)


@app.route('/assign_task/<int:volunteer_id>', methods=['GET', 'POST'])
def assign_task(volunteer_id):
    if 'admin_username' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':
        task = request.form.get('Task')
        # Logic to assign the task to the volunteer
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO tasks (volunteer_id, task)
            VALUES (?, ?)
        ''', (volunteer_id, task))
        conn.commit()
        conn.close()

        flash(f'Task "{task}" assigned to volunteer ID: {volunteer_id}!', 'success')
        return redirect('/admin_dashboard')

    return render_template('assign_task.html', volunteer_id=volunteer_id)


@app.route('/logout')
def logout():
    session.pop('admin_username', None)
    session.pop('volunteer_id', None)
    return redirect('/')


if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
