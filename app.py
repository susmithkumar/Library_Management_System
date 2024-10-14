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
        role = request.form['role']
        address = request.form['address']
        #chnages vinod
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT MAX(sno) FROM users")  # Get the latest `sno`
        result = cursor.fetchone()
        sno = result[0] + 1 if result[0] else 1  # Increment the `sno` for the new user
        # Combine `sno` and `first name` to create the `userid`
        userid = f"{userName.lower()}{sno}"
        #completed my changes
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
            cursor.execute('INSERT INTO user_table (first_name, email, password, userid, address) VALUES (%s, %s, %s)', (userName, email, hashed_password, userid, address))#added by vinod userid, address
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
#update the users vinod
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
            # Fetch updated details from the form
            updated_name = request.form['name']
            updated_email = request.form['email']
            updated_address = request.form['address']
            updated_role = request.form['role']

            # Update only if valid email
            if not re.match(r'[^@]+@[^@]+\.[^@]+', updated_email):
                flash('Invalid email address!')
            else:
                # Update the user profile in the database
                cursor.execute('UPDATE user_table SET first_name = %s, email = %s, address = %s, role = %s WHERE id = %s',
                               (updated_name, updated_email, updated_address, updated_role, session['userid']))
                mysql.connection.commit()
                flash('Profile updated successfully!')
                return redirect(url_for('dashboard'))

        # GET request: Fetch current user data to pre-fill the form
        cursor.execute('SELECT * FROM user_table WHERE id = %s', (session['userid'],))
        user = cursor.fetchone()
        return render_template('update_profile.html', user=user)
    return redirect(url_for('login'))
#vinod chnages done
@app.route("/view_user", methods =['GET', 'POST'])
def view_user():
    ##new changes by vinod
    if 'loggedin' in session:
        viewUserId = request.args.get('id') or session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE id = %s', (viewUserId,))
        user = cursor.fetchone()
        
        # Debugging statements
        if not user:
            print("User not found in the database")
        else:
            print(f"User fetched: {user}")

        if user:
            return render_template("view_user.html", user=user)
        else:
            flash('User not found')
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))
#changes completed by vinod
'''if 'loggedin' in session:
        viewUserId = request.args.get('id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print(viewUserId)
        print(session['user_id'])
        cursor.execute('SELECT * FROM user_table WHERE id = % s', (session['user_id'], ))
        user = cursor.fetchone()
        print(user)
        return render_template("view_user.html", user = user)
    return redirect(url_for('login'))'''
  

if __name__ == '__main__':
    app.run(debug=True)
