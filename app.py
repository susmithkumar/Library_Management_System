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
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = None
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        print("Executing query: SELECT * FROM user_table WHERE email = %s", (email,))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['user_id'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            mesage = 'Incorrect email or password!'
    return render_template('login.html', mesage=mesage)


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        email = request.form['email']
        role = None
        address = request.form['address']
        last_name=request.form['last_name']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            mesage = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address!'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user_table (first_name, email, password,address, role,last_name) VALUES (%s, %s,%s, %s, %s, %s)', 
                           (userName, email, hashed_password, address, role,last_name))
            mysql.connection.commit()
            mesage = 'You have successfully registered!'

            # Get the latest `sno` for unique userid generation
            userid = cursor.lastrowid
            sno = f'LB{userid}'
            cursor.execute('UPDATE user_table SET userid = %s WHERE id = %s', (sno, userid))
            mysql.connection.commit()
    elif request.method == 'POST':
        mesage = 'Please fill out the form!'
    return render_template('register.html', mesage=mesage)


@app.route("/users", methods =['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table')
        users = cursor.fetchall()
        return render_template("users.html", users=users)
    return redirect(url_for('login'))
#chnages strted by vinod
@app.route("/save_user", methods=['GET', 'POST'])
def save_user():
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'role' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            role = request.form['role']
            action = request.form['action']
            
            if action == 'updateUser':
                userId = request.form['userid']
                cursor.execute('UPDATE user_table SET first_name=%s, last_name=%s, email=%s, role=%s WHERE id=%s',
                               (first_name, last_name, email, role, userId))
                mysql.connection.commit()
                flash('User updated successfully!')
            else:
                password = request.form['password']
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute('INSERT INTO user_table (first_name, last_name, email, password, role) VALUES (%s, %s, %s, %s, %s)',
                               (first_name, last_name, email, hashed_password, role))
                mysql.connection.commit()
                flash('User created successfully!')
            return redirect(url_for('users'))
        
        return redirect(url_for('users'))
    return redirect(url_for('login'))

@app.route("/edit_user", methods=['GET', 'POST'])
def edit_user():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE id = %s', (editUserId, ))  # Changed to user_table
        user_details = cursor.fetchone()  # Fetch only one user since we're editing
        
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            role = request.form['role']
            userId = request.form['userid']
            cursor.execute('UPDATE user_table SET first_name=%s, last_name=%s, email=%s, role=%s WHERE id=%s',
                           (first_name, last_name, email, role, userId))
            mysql.connection.commit()
            flash('User updated successfully!')
            return redirect(url_for('users'))
        
        return render_template("edit_user.html", user=user_details)
    return redirect(url_for('login'))
#changes by vinod

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form:
            updated_first_name = request.form['first_name']
            updated_last_name = request.form['last_name']
            updated_email = request.form['email']
            updated_address = request.form['address'] if 'address' in request.form else None
            updated_role = request.form['role']  # Ensure role is passed and handled

            # Ensure valid email
            if not re.match(r'[^@]+@[^@]+\.[^@]+', updated_email):
                flash('Invalid email address!')
            else:
                # Update first name, last name, email, address (not the role, unless admin)
                cursor.execute('UPDATE user_table SET first_name = %s, last_name = %s, email = %s, address = %s WHERE id = %s',
                               (updated_first_name, updated_last_name, updated_email, updated_address, session['userid']))
                mysql.connection.commit()
                flash('Profile updated successfully!')
                return redirect(url_for('dashboard'))

        # Retrieve user information to pre-fill the form
        cursor.execute('SELECT * FROM user_table WHERE id = %s', (session['userid'],))
        user = cursor.fetchone()
        return render_template('update_profile.html', user=user)
    
    return redirect(url_for('login'))

#chanegs by vinod done

@app.route('/view_user', methods=['GET'])
def view_user():
    if 'loggedin' in session:
        viewUserId = request.args.get('id') or session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE id = %s', (viewUserId,))
        user = cursor.fetchone()

        if not user:
            flash('User not found')
            return redirect(url_for('dashboard'))

        # Check if the logged-in user has role 'none' or is viewing their own profile
        is_editable = session['userid'] == viewUserId or session['role'] == 'none'

        return render_template("view_user.html", user=user, is_editable=is_editable)
    return redirect(url_for('login'))

# Add Book Route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    mesage = ''
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
            mesage = 'Book added successfully!'
        else:
            mesage = 'Please fill out this form!'

        return render_template('add_book.html', mesage=mesage)
    return redirect(url_for('login'))

# View Books Route
@app.route('/view_books', methods=['GET'])
def view_books():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM add_book')
        books = cursor.fetchall()  # Fetch all books
        return render_template('view_books.html', books=books)
    return redirect(url_for('login'))

# Edit Book Route
@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    mesage = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            rack = request.form['rack']
            quantity = request.form['quantity']

            # Update book details in the database
            cursor.execute('UPDATE add_book SET title = %s, author = %s, rack = %s, quantity = %s WHERE id = %s',
                           (title, author, rack, quantity, id))
            mysql.connection.commit()
            mesage = 'Book updated successfully!'
            return redirect(url_for('view_books', mesage=mesage))

        # Fetch the book details for the given ID
        cursor.execute('SELECT * FROM add_book WHERE id = %s', (id,))
        book = cursor.fetchone()

        return render_template('edit_book.html', book=book)
    return redirect(url_for('login'))


#my changes dhanesh 



if __name__ == '__main__':
    app.run(debug=True)
