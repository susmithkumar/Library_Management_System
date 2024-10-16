from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors  # Needed for working with MySQL cursors
import os
import re
import bcrypt

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Configure MySQL database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL user
app.config['MYSQL_PASSWORD'] = 'W7301@jqir#'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'library_management_system'

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        print(email,password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE email = % s', (email,))
        user = cursor.fetchone()
        print(user)
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['role'] = user['role']
            mesage = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user_table (first_name, email, password) VALUES (%s, %s, %s)', (userName, email, hashed_password))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)

# Add Book Route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'loggedin' in session:  # Ensure the user is logged in
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            rack = request.form['rack']
            quantity = request.form['quantity']

            # Insert book data into the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO add_book (title, author, rack, quantity) VALUES (%s, %s, %s, %s)',
                           (title, author, rack, quantity))
            mysql.connection.commit()
            # Get the ID of the newly inserted user
            new_user_id = cursor.lastrowid

            # Create user_code as 'BK' + new_user_id
            user_code = f'BK{new_user_id}'

            # Update the user_code column with the generated code
            cursor.execute('UPDATE add_book SET isbn = %s WHERE id = %s', (user_code, new_user_id))
            
            # Commit the update
            mysql.connection.commit()
            flash('Book added successfully!')
            return redirect(url_for('dashboard'))

        return render_template('add_book.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
