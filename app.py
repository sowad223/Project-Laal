from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management


# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Replace with your host
            database='flask_app',  # Replace with your database name
            user='projectlaal',  # Replace with your username
            password='sowadrahman'  # Replace with your password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# Database setup function
def init_db():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()

        # Create donations table
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS donations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            address TEXT NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create volunteers table
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS volunteers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            skills TEXT,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create admin table
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS admin (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        )
        ''')

        # Create tasks table
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            volunteer_id INT,
            task TEXT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (volunteer_id) REFERENCES volunteers (id)
        )
        ''')

        # Insert default admin if it doesn't exist
        cursor.execute('SELECT * FROM admin WHERE username = %s', ('sowadrahman',))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO admin (username, password) VALUES (%s, %s)',
                           ('sowadrahman', generate_password_hash('projectlaal')))

        conn.commit()
        cursor.close()
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
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO donations (name, email, phone, address, payment_method)
                VALUES (%s, %s, %s, %s, %s)
            ''', (name, email, phone, address, payment_method))
            conn.commit()
            cursor.close()
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

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert the volunteer into the database
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO volunteers (name, email, phone, skills, password)
                VALUES (%s, %s, %s, %s, %s)
            ''', (name, email, phone, skills, hashed_password))
            conn.commit()
            cursor.close()
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
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM volunteers WHERE email = %s', (email,))
            volunteer = cursor.fetchone()
            cursor.close()
            conn.close()

            if volunteer and check_password_hash(volunteer[5], password):  # Check hashed password
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
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE volunteer_id = %s', (volunteer_id,))
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('volunteer_dashboard.html', tasks=tasks)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')

        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM admin WHERE username = %s', (username,))
            admin = cursor.fetchone()
            cursor.close()
            conn.close()

            if admin and check_password_hash(admin[1], password):  # Check hashed password
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

    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM volunteers')
        volunteers = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('admin_dashboard.html', volunteers=volunteers)


@app.route('/assign_task/<int:volunteer_id>', methods=['GET', 'POST'])
def assign_task(volunteer_id):
    if 'admin_username' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':
        task = request.form.get('Task')
        # Logic to assign the task to the volunteer
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO tasks (volunteer_id, task)
                VALUES (%s, %s)
            ''', (volunteer_id, task))
            conn.commit()
            cursor.close()
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
