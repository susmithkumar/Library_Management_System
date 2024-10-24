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

def create_schema():
    with app.app_context():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            with open('schema.sql', 'r') as f:
                sql = f.read()
                sql_statements = sql.split(';')
                for statement in sql_statements:
                    if statement.strip():  # Ignore empty statements
                        cursor.execute(statement)
                        mysql.connection.commit()
            print("Schema created successfully!")
        except mysql.connection.Error as err:
            print("Failed creating schema: {}".format(err))
        finally:
            cursor.close()


@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
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
            
            # Check if 'active' key exists in user dictionary
            if 'active' in user:
                session['active'] = user['active']
            else:
                # Set a default value or skip setting this session variable
                session['active'] = True  # or whatever default value you want
            
            # Fetch responsibilities (and paths) linked to the user's role
            cursor.execute("""
            SELECT r.name AS responsibility_name, r.path AS responsibility_path
            FROM responsibilities r
            JOIN roles_responsibilities rr ON r.id = rr.responsibility_id
            WHERE rr.role_id = %s
            """, (session['role'],))
            
            # Store the responsibilities (menu links) in the session for use in the left menu
            session['responsibilities'] = cursor.fetchall()
            
            mesage = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            mesage = 'Incorrect email or password!'
    return render_template('login.html', mesage=mesage)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get total books count
        cursor.execute('SELECT SUM(quantity) as total_books FROM add_book')
        total_books = cursor.fetchone()['total_books'] or 0
        
        # Get available books count
        cursor.execute('SELECT SUM(quantity) as available_books FROM add_book WHERE quantity > 0')
        available_books = cursor.fetchone()['available_books'] or 0
        
        # Get issued books count
        cursor.execute('SELECT COUNT(*) as issued_books FROM book_issues WHERE is_returned = FALSE')
        issued_books = cursor.fetchone()['issued_books'] or 0
        
        # Get returned books count
        cursor.execute('SELECT COUNT(*) as returned_books FROM book_issues WHERE is_returned = TRUE')
        returned_books = cursor.fetchone()['returned_books'] or 0
        
        return render_template("dashboard.html", 
                               total_books=total_books,
                               available_books=available_books,
                               issued_books=issued_books,
                               returned_books=returned_books)
    return redirect(url_for('login'))

@app.route('/search_books', methods=['POST'])
def search_books():
    search_term = request.form.get('search_term')
    if search_term:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch books that match the search term in title or author
        cursor.execute('''
            SELECT * FROM add_book 
            WHERE title LIKE %s OR author LIKE %s
        ''', ('%' + search_term + '%', '%' + search_term + '%'))
        results = cursor.fetchall()

        # Get total books count
        cursor.execute('SELECT SUM(quantity) as total_books FROM add_book')
        total_books = cursor.fetchone()['total_books'] or 0
        
        # Get available books count
        cursor.execute('SELECT SUM(quantity) as available_books FROM add_book WHERE quantity > 0')
        available_books = cursor.fetchone()['available_books'] or 0
        
        # Get issued books count
        cursor.execute('SELECT COUNT(*) as issued_books FROM book_issues WHERE is_returned = FALSE')
        issued_books = cursor.fetchone()['issued_books'] or 0
        
        # Get returned books count
        cursor.execute('SELECT COUNT(*) as returned_books FROM book_issues WHERE is_returned = TRUE')
        returned_books = cursor.fetchone()['returned_books'] or 0

        cursor.close()
        return render_template('dashboard.html', search_results=results, search_term=search_term, total_books=total_books,
                               available_books=available_books,
                               issued_books=issued_books,
                               returned_books=returned_books)
    return redirect(url_for('dashboard'))

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
        role = f'2'
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
                           (userName, email, hashed_password, address, role, last_name))
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
        cursor.execute('SELECT u.id, u.first_name, u.email, u.role, r.name as role_name FROM user_table u JOIN roles r ON u.role = r.id')
        users = cursor.fetchall()

        # Fetch all available roles
        cursor.execute('SELECT id, name FROM roles')
        roles = cursor.fetchall()
        return render_template("users.html", users=users, roles=roles)
    return redirect(url_for('login'))

@app.route("/user_roles", methods =['GET', 'POST'])
def user_roles():
    if 'loggedin' in session:
        user_id = request.form.get('user_id')
        role_id = request.form.get('role_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE user_table SET role = %s WHERE id = %s', (role_id, user_id))
        mysql.connection.commit()
        cursor.execute('SELECT u.id, u.first_name, u.email, u.role, r.name as role_name FROM user_table u JOIN roles r ON u.role = r.id')
        users = cursor.fetchall()

        # Fetch all available roles
        cursor.execute('SELECT id, name FROM roles')
        roles = cursor.fetchall()
        return render_template("users.html", users=users, roles=roles)

    return redirect(url_for('login'))




#chnages strted by vinod
@app.route("/save_user", methods=['GET', 'POST'])
def save_user():
    mesage = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            address = request.form['address']
            cursor.execute('UPDATE user_table SET first_name=%s, last_name=%s, email=%s, address=%s WHERE id=%s',
                           (first_name, last_name, email, address, session['user_id']))
            mysql.connection.commit()
            return redirect(url_for('view_user'))
        
        return redirect(url_for('view_user'))
    return redirect(url_for('login'))

@app.route("/edit_user", methods=['GET', 'POST'])
def edit_user():
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE id = %s', (editUserId, ))  # Changed to user_table
        user_details = cursor.fetchone()  # Fetch only one user since we're editing
        return render_template("edit_user.html", user=user_details)
    return redirect(url_for('login'))


@app.route("/password_change", methods=['GET', 'POST'])
def password_change():
    if 'loggedin' in session:
        if request.method == 'POST':
            password = request.form['password']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE user_table SET password=%s WHERE id = %s', (hashed_password,session['user_id'], ))  # Changed to user_table
            mysql.connection.commit()
            mesage="password updated successfully please login again"
            return render_template('login.html', mesage=mesage)
        else:
            return render_template("password_change.html")
    return redirect(url_for('login'))
@app.route('/view_user', methods=['GET'])
def view_user():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('''SELECT * , r.name AS role_name
        FROM user_table u
        LEFT JOIN roles r ON u.role = r.id WHERE u.id = % s''', (session['user_id'], ))
        user = cursor.fetchone()
        return render_template("view_user.html", user = user)
    return redirect(url_for('login'))


@app.route('/add_role', methods=['GET', 'POST'])
def add_role():
    mesage = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch all responsibilities to display in the form
    cursor.execute("SELECT * FROM responsibilities")
    all_responsibilities = cursor.fetchall()

    if request.method == 'POST':
        role_name = request.form.get('role')
        role_description = request.form.get('description')
        selected_responsibilities = request.form.getlist('responsibilities')  # List of selected responsibility IDs

        if not role_name:
            message = "Role name is required!", "danger"
            return render_template('add_role.html', all_responsibilities=all_responsibilities)


        cursor.execute("""CREATE TABLE IF NOT EXISTS roles (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(100) NOT NULL,
        description TEXT)""")
        # Insert the new role into the roles table
        cursor.execute("""INSERT INTO roles (name, description) VALUES (%s, %s)""", (role_name, role_description))

        # Fetch the newly created role's ID
        role_id = cursor.lastrowid

        # Insert selected responsibilities into the roles_responsibilities table
        for responsibility_id in selected_responsibilities:
            cursor.execute("""
                INSERT INTO roles_responsibilities (role_id, responsibility_id) 
                VALUES (%s, %s)
            """, (role_id, responsibility_id))

        mysql.connection.commit()
        message = f"Role '{role_name}' added successfully!", "success"
        return redirect(url_for('roles'))

    return render_template('add_role.html', all_responsibilities=all_responsibilities)

@app.route('/edit_role/<int:role_id>', methods=['GET', 'POST'])
def edit_role(role_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch the current role details
    cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
    role = cursor.fetchone()

    # Fetch all responsibilities
    cursor.execute("SELECT * FROM responsibilities")
    all_responsibilities = cursor.fetchall()

    # Fetch current responsibilities for this role
    cursor.execute("SELECT responsibility_id FROM roles_responsibilities WHERE role_id = %s", (role_id,))
    current_responsibilities = [row['responsibility_id'] for row in cursor.fetchall()]

    if request.method == 'POST':
        role_name = request.form.get('name')
        role_description = request.form.get('description')
        selected_responsibilities = request.form.getlist('responsibilities')  # List of selected responsibilities (ids)

        if not role_name:
            mesage = "Role name is required!", "danger"
            return redirect(url_for('edit_role', role_id=role_id))

        # Update the role's name and description
        cursor.execute("""
                UPDATE roles SET name = %s, description = %s WHERE id = %s""", (role_name, role_description, role_id))

        # Clear existing responsibilities
        cursor.execute("DELETE FROM roles_responsibilities WHERE role_id = %s", (role_id,))

        # Insert new responsibilities
        for responsibility_id in selected_responsibilities:
            cursor.execute("INSERT INTO roles_responsibilities (role_id, responsibility_id) VALUES (%s, %s)", (role_id, responsibility_id))

        mysql.connection.commit()
        mesage = f"Role '{role_name}' updated successfully!", "success"
        return redirect(url_for('roles'))

    return render_template('edit_role.html', role=role, all_responsibilities=all_responsibilities, current_responsibilities=current_responsibilities)


@app.route('/roles', methods=['GET'])
def roles():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
         SELECT r.id AS role_id, r.name AS role_name, r.description, 
               GROUP_CONCAT(res.name SEPARATOR ', ') AS responsibility_names
        FROM roles r
        LEFT JOIN roles_responsibilities rr ON r.id = rr.role_id
        LEFT JOIN responsibilities res ON rr.responsibility_id = res.id
        GROUP BY r.id, r.name, r.description""",)
    roles = cursor.fetchall()
    print(roles)
    return render_template('roles.html', roles=roles)


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
            return render_template('add_book.html', mesage=mesage)
        else:
            mesage = 'Please fill out this form!'
            return render_template('add_book.html', mesage=mesage)
    return redirect(url_for('login'))

# View Books Route
@app.route('/books', methods=['GET'])
def books():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM add_book')
        books = cursor.fetchall()  # Fetch all books
        return render_template('books.html', books=books)
    return redirect(url_for('login'))

@app.route('/books', methods=['GET'])
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

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            issue_id = request.form['issue_id']
            return_date = request.form['return_date']
            
            # Mark the book as returned
            cursor.execute('UPDATE book_issues SET is_returned = TRUE, return_date = %s WHERE id = %s',
                           (return_date, issue_id))
            # Increase the book quantity
            cursor.execute('''
                UPDATE add_book 
                SET quantity = quantity + 1 
                WHERE id = (SELECT book_id FROM book_issues WHERE id = %s)
            ''', (issue_id,))
            mysql.connection.commit()
            flash('Book returned successfully!')
            return redirect(url_for('return_book'))
        
        # Fetch issued books that haven't been returned
        cursor.execute('''
            SELECT bi.id, u.first_name, u.last_name, b.title, bi.issue_date 
            FROM book_issues bi 
            JOIN user_table u ON bi.user_id = u.id 
            JOIN add_book b ON bi.book_id = b.id 
            WHERE bi.is_returned = FALSE
        ''')
        issued_books = cursor.fetchall()
        return render_template('return_book.html', issued_books=issued_books)
    return redirect(url_for('login'))

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            user_id = request.form['user_id']
            book_id = request.form['book_id']
            issue_date = request.form['issue_date']
            
            # Check if the book is already issued to the user
            cursor.execute('SELECT * FROM book_issues WHERE user_id = %s AND book_id = %s AND return_date IS NULL', (user_id, book_id))
            existing_issue = cursor.fetchone()
            
            if existing_issue:
                flash('This book is already issued to the user!')
            else:
                # Check if the book is available
                cursor.execute('SELECT quantity FROM add_book WHERE id = %s', (book_id,))
                book = cursor.fetchone()
                if book and book['quantity'] > 0:
                    # Issue the book
                    cursor.execute('INSERT INTO book_issues (user_id, book_id, issue_date) VALUES (%s, %s, %s)',
                                   (user_id, book_id, issue_date))
                    # Decrease the book quantity
                    cursor.execute('UPDATE add_book SET quantity = quantity - 1 WHERE id = %s', (book_id,))
                    mysql.connection.commit()
                    flash('Book issued successfully!')
                else:
                    flash('Book not available!')
            return redirect(url_for('issue_book'))
        
        # Fetch users and available books for the form
        cursor.execute('SELECT id, first_name, last_name FROM user_table')
        users = cursor.fetchall()
        cursor.execute('SELECT id, title FROM add_book WHERE quantity > 0')
        books = cursor.fetchall()
        return render_template('issue_book.html', users=users, books=books)
    return redirect(url_for('login'))

@app.route('/issued_books')
def issued_books():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT bi.id, b.title, bi.issue_date 
            FROM book_issues bi 
            JOIN add_book b ON bi.book_id = b.id 
            WHERE bi.user_id = %s AND bi.return_date IS NULL
        ''', (session['user_id'],))
        issued_books = cursor.fetchall()
        return render_template('issued_books.html', issued_books=issued_books)
    return redirect(url_for('login'))

import requests
import random
import time

def populate_books_table():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Check current book count
    cursor.execute("SELECT COUNT(*) as count FROM add_book")
    count = cursor.fetchone()['count']
    
    if count < 100:
        books_to_add = 100 - count
        total_books_added = 0
        
        while total_books_added < books_to_add:
            # Use a random letter to get varied results
            query = random.choice(['a', 'e', 'i', 'o', 'u', 'y'])
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40"
            
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                books = response.json().get('items', [])
                
                for book in books:
                    if total_books_added >= books_to_add:
                        break
                    
                    volume_info = book.get('volumeInfo', {})
                    title = volume_info.get('title', 'Unknown Title')[:255]
                    authors = ', '.join(volume_info.get('authors', ['Unknown Author']))[:255]
                    isbn = volume_info.get('industryIdentifiers', [{}])[0].get('identifier', 'Unknown ISBN')[:20]
                    rack = f"Rack-{random.randint(1, 100)}"
                    quantity = random.randint(1, 10)
                    
                    cursor.execute('''
                    INSERT INTO add_book (title, author, rack, quantity, isbn)
                    VALUES (%s, %s, %s, %s, %s)
                    ''', (title, authors, rack, quantity, isbn))
                    
                    total_books_added += 1
                
                mysql.connection.commit()
                
                # Add a delay between requests to avoid rate limiting
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                break
        
        print(f"Added {total_books_added} books to the database.")
    else:
        print("The books table already has 100 or more entries.")
    
    cursor.close()

def assign_books_to_users():
    with app.app_context():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get users
        cursor.execute('SELECT id FROM user_table LIMIT 7')
        users = cursor.fetchall()
        
        # Get available books
        cursor.execute('SELECT id FROM add_book WHERE quantity > 0 LIMIT 7')
        books = cursor.fetchall()
        
        for user in users:
            for book in books:
                # Check if the book is already issued to the user
                cursor.execute('SELECT * FROM book_issues WHERE user_id = %s AND book_id = %s AND return_date IS NULL', (user['id'], book['id']))
                existing_issue = cursor.fetchone()
                
                if not existing_issue:
                    # Issue the book
                    cursor.execute('INSERT INTO book_issues (user_id, book_id, issue_date) VALUES (%s, %s, CURDATE())',
                                   (user['id'], book['id']))
                    # Decrease the book quantity
                    cursor.execute('UPDATE add_book SET quantity = quantity - 1 WHERE id = %s', (book['id'],))
                    break  # Move to the next user after issuing one book
        
        mysql.connection.commit()
        print("Books assigned to users successfully!")


# Call this function when your app starts
if __name__ == '__main__':
    create_schema()
    with app.app_context():
        populate_books_table()
        assign_books_to_users()
    app.run(debug=True)
