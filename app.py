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
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'W7301@jqir#'
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
    mesage = None
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
            session['user_id'] = user['id']
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



@app.route("/users", methods =['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table')
        users = cursor.fetchall()
        return render_template("users.html", users = users)
    return redirect(url_for('login'))

@app.route("/view_user", methods =['GET', 'POST'])
def view_user():
    if 'loggedin' in session:
        viewUserId = request.args.get('id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print(viewUserId)
        print(session['user_id'])
        cursor.execute('SELECT * FROM user_table WHERE id = % s', (session['user_id'], ))
        user = cursor.fetchone()
        print(user)
        return render_template("view_user.html", user = user)
    return redirect(url_for('login'))


@app.route('/add_role', methods=['GET', 'POST'])
def add_role():
    mesage = ''
    if request.method == 'POST' and 'role' in request.form and 'description' in request.form:
        role_name = request.form.get('role')
        role_description = request.form.get('description')

        # Check if the role name is empty
        if not role_name:
            mesage = 'Role name is required!'
            return render_template('add_role.html', mesage=mesage)

        # Connect to the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the roles table exists and create it if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            );
        """)
        mysql.connection.commit()
        print("Table successfully created (if it didn't exist).")

        # Check if the role already exists
        cursor.execute('SELECT * FROM roles WHERE name = %s', (role_name,))
        role = cursor.fetchone()

        if role:
            mesage = 'Role already exists!'
        else:
            # Insert the new role
            cursor.execute('INSERT INTO roles (name, description) VALUES (%s, %s)', (role_name, role_description))
            mysql.connection.commit()
            mesage = 'Role created successfully!'

        # Close the cursor after usage
        cursor.close()

    elif request.method == 'POST':
        mesage = 'Please fill out the form!'

    # Render the form with a success or error message
    return render_template('add_role.html', mesage=mesage)


@app.route('/edit_role/<int:role_id>', methods=['GET', 'POST'])
def edit_role(role_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Handle GET request (Display edit form)
    if request.method == 'GET':
        cursor.execute('SELECT * FROM roles WHERE id = %s', (role_id,))
        role = cursor.fetchone()
        if not role:
            mesage ='Role not found!'
            return redirect(url_for('roles'))
        return render_template('edit_role.html', role=role)

    # Handle POST request (Update the role)
    if request.method == 'POST':
        role_name = request.form['name']
        role_description = request.form['description']

        if not role_name or not role_description:
            mesage ='Please fill in all fields!'
            return redirect(url_for('edit_role', role_id=role_id))

        # Update the role details in the database
        cursor.execute('UPDATE roles SET name = %s, description = %s WHERE id = %s',
                       (role_name, role_description, role_id))
        mysql.connection.commit()
        mesage ='Role updated successfully!'
        return redirect(url_for('roles'))

@app.route('/roles', methods=['GET'])
def roles():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM roles')
    roles = cursor.fetchall()
    return render_template('roles.html', role=roles)


@app.route('/add_responsibility', methods=['GET', 'POST'])
def add_responsibility():
    mesage = ''
    if request.method == 'POST' and 'responsibility' in request.form and 'description' in request.form and 'path' in request.form:
        responsibility_name = request.form.get('responsibility')
        responsibility_description = request.form.get('description')
        responsibility_path = request.form.get('path')

        # Check if the responsibility name is empty
        if not responsibility_name:
            mesage = 'Responsibility name is required!'
            return render_template('add_responsibility.html', mesage=mesage)

        # Connect to the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the responsibilities table exists and create it if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responsibilities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                path VARCHAR(255)
            );
        """)
        mysql.connection.commit()
        print("Table successfully created (if it didn't exist).")

        # Check if the responsibility already exists
        cursor.execute('SELECT * FROM responsibilities WHERE name = %s', (responsibility_name,))
        responsibility = cursor.fetchone()

        if responsibility:
            mesage = 'Responsibility already exists!'
        else:
            # Insert the new responsibility with the path
            cursor.execute('INSERT INTO responsibilities (name, description, path) VALUES (%s, %s, %s)',
                           (responsibility_name, responsibility_description, responsibility_path))
            mysql.connection.commit()
            mesage = 'Responsibility created successfully!'

        # Close the cursor after usage
        cursor.close()

    elif request.method == 'POST':
        mesage = 'Please fill out the form!'

    # Render the form with a success or error message
    return render_template('add_responsibility.html', mesage=mesage)


@app.route('/responsibility', methods=['GET'])
def responsibility():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM responsibilities')
    responsibilities = cursor.fetchall()
    cursor.close()
    return render_template('responsibility.html', responsibility=responsibilities)

@app.route('/edit_responsibility/<int:responsibility_id>', methods=['GET', 'POST'])
def edit_responsibility(responsibility_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Handle GET request (Display the form with existing data)
    if request.method == 'GET':
        cursor.execute('SELECT * FROM responsibilities WHERE id = %s', (responsibility_id,))
        responsibility = cursor.fetchone()
        if not responsibility:
            mesage ='Responsibility not found!'
            return redirect(url_for('view_responsibilities'))
        return render_template('edit_responsibility.html', responsibility=responsibility)

    # Handle POST request (Update the responsibility in the database)
    if request.method == 'POST':
        responsibility_name = request.form['responsibility']
        responsibility_description = request.form['description']
        responsibility_path = request.form['path']

        if not responsibility_name or not responsibility_description or not responsibility_path:
            mesage ='Please fill in all fields!'
            return redirect(url_for('edit_responsibility', responsibility_id=responsibility_id))

        cursor.execute('UPDATE responsibilities SET name = %s, description = %s, path = %s WHERE id = %s',
                       (responsibility_name, responsibility_description, responsibility_path, responsibility_id))
        mysql.connection.commit()
        cursor.close()
        mesage ='Responsibility updated successfully!'
        return redirect(url_for('responsibility'))

if __name__ == '__main__':
    app.run(debug=True)
