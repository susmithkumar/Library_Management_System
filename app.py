from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors  # Needed for working with MySQL cursors
import re, bcrypt, requests, random, time, os
import openai
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
import json
import numpy as np
from werkzeug.utils import secure_filename
from scipy.spatial.distance import cosine
from dotenv import load_dotenv


app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')
engine = create_engine("mysql+pymysql://root:PASSWORD@localhost/library_management_system")
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


# Set the upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Optionally, limit the maximum size of uploaded files (e.g., 2 MB)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure MySQL database connection
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'PASSWORD'
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
            if 'cursor' in locals():  # Ensure cursor exists before closing
                cursor.close()


@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE email = %s AND active = 1', (email,))
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
            
            flash("Logged in successfully !", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect email or password!", "danger")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get total books count
        cursor.execute('SELECT SUM(quantity) as total_books FROM add_book')
        total_books = cursor.fetchone()['total_books'] or 0

        # Get issued books count
        cursor.execute('SELECT COUNT(*) as issued_books FROM book_issues WHERE is_returned = FALSE')
        issued_books = cursor.fetchone()['issued_books'] or 0

        available_books = total_books - issued_books

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
    if 'loggedin' in session:
        search_term = request.form.get('search_term')
        if search_term:
            # Generate embedding for the search term
            query_embedding = openai.Embedding.create(input=search_term, model="text-embedding-ada-002")['data'][0]['embedding']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Fetch all book embeddings from the database
            cursor.execute('SELECT id, title, author, embedding FROM add_book')
            books = cursor.fetchall()

            # Calculate cosine similarity between the query embedding and each book embedding
            results = []
            for book in books:
                if book['embedding']:  # Ensure the embedding is not null
                    # Parse JSON embedding (from JSON string to Python list of floats)
                    book_embedding = np.array(json.loads(book['embedding']))

                    # Calculate cosine similarity
                    similarity = 1 - cosine(query_embedding, book_embedding)
                    results.append((similarity, book))

            # Sort results by similarity in descending order
            results.sort(reverse=True, key=lambda x: x[0])

            # Retrieve top N results (e.g., top 10)
            top_results = [book for _, book in results[:10]]

            # Get additional statistics
            cursor.execute('SELECT SUM(quantity) as total_books FROM add_book')
            total_books = cursor.fetchone()['total_books'] or 0

            cursor.execute('SELECT COUNT(*) as issued_books FROM book_issues WHERE is_returned = FALSE')
            issued_books = cursor.fetchone()['issued_books'] or 0

            available_books = total_books - issued_books

            cursor.execute('SELECT COUNT(*) as returned_books FROM book_issues WHERE is_returned = TRUE')
            returned_books = cursor.fetchone()['returned_books'] or 0

            cursor.close()
            return render_template('dashboard.html', search_results=top_results, search_term=search_term,
                                   total_books=total_books, available_books=available_books,
                                   issued_books=issued_books, returned_books=returned_books)
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

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
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not userName or not password or not email:
            flash("Please fill out the form!", "danger")
        else:
            cursor.execute('INSERT INTO user_table (first_name, email, password,address, role,last_name) VALUES (%s, %s,%s, %s, %s, %s)', 
                           (userName, email, hashed_password, address, role, last_name))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")

            # Get the latest `sno` for unique userid generation
            userid = cursor.lastrowid
            sno = f'LB{userid}'
            cursor.execute('UPDATE user_table SET userid = %s WHERE id = %s', (sno, userid))
            mysql.connection.commit()
    elif request.method == 'POST':
        flash("'Please fill out the form!", "danger")
    return render_template('register.html')




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
            flash("password updated successfully please login again", "success")
            return render_template('login.html')
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
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch all responsibilities to display in the form
        cursor.execute("SELECT * FROM responsibilities")
        all_responsibilities = cursor.fetchall()

        if request.method == 'POST':
            role_name = request.form.get('role')
            role_description = request.form.get('description')
            selected_responsibilities = request.form.getlist('responsibilities')  # List of selected responsibility IDs

            if not role_name:
                flash("Role name is required!", "danger")
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
            flash("Role '{role_name}' added successfully!", "success")
            return redirect(url_for('roles'))

        return render_template('add_role.html', all_responsibilities=all_responsibilities)
    return redirect(url_for('login'))


@app.route('/edit_role/<int:role_id>', methods=['GET', 'POST'])
def edit_role(role_id):
    
    if 'loggedin' in session:  # Ensure the user is logged in
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
                flash("Role name is required!", "danger")
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
            flash("Role '{role_name}' updated successfully!", "success")
            return redirect(url_for('roles'))

        return render_template('edit_role.html', role=role, all_responsibilities=all_responsibilities, current_responsibilities=current_responsibilities)
    return redirect(url_for('login'))

@app.route('/roles', methods=['GET'])
def roles():
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT r.id AS role_id, r.name AS role_name, r.description, 
                GROUP_CONCAT(res.name SEPARATOR ', ') AS responsibility_names
            FROM roles r
            LEFT JOIN roles_responsibilities rr ON r.id = rr.role_id
            LEFT JOIN responsibilities res ON rr.responsibility_id = res.id
            GROUP BY r.id, r.name, r.description""",)
        roles = cursor.fetchall()
        
        return render_template('roles.html', roles=roles)
    return redirect(url_for('login'))


@app.route('/role_delete/<int:role_id>', methods=['GET'])
def role_delete(role_id):
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # First, delete entries from the roles_responsibilities table
        cursor.execute("DELETE FROM roles_responsibilities WHERE role_id = %s", (role_id,))
        cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
        mysql.connection.commit()
        flash("Role Deleted updated successfully!", "danger")
        return redirect(url_for('roles'))
    return redirect(url_for('login'))


@app.route('/add_responsibility', methods=['GET', 'POST'])
def add_responsibility():
    
    if 'loggedin' in session:  # Ensure the user is logged in
    
        if request.method == 'POST' and 'responsibility' in request.form and 'description' in request.form and 'path' in request.form:
            responsibility_name = request.form.get('responsibility')
            responsibility_description = request.form.get('description')
            responsibility_path = request.form.get('path')

            # Check if the responsibility name is empty
            if not responsibility_name:
                flash("Responsibility name is required!", "danger")
                return render_template('add_responsibility.html')

            # Connect to the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check if the responsibility already exists
            cursor.execute('SELECT * FROM responsibilities WHERE name = %s', (responsibility_name,))
            responsibility = cursor.fetchone()

            if responsibility:
                flash("Responsibility already exists!", "danger")
            else:
                # Insert the new responsibility with the path
                cursor.execute('INSERT INTO responsibilities (name, description, path) VALUES (%s, %s, %s)',
                            (responsibility_name, responsibility_description, responsibility_path))
                mysql.connection.commit()
                flash("Responsibility Created Successfully", "success")
            # Close the cursor after usage
            cursor.close()

        elif request.method == 'POST':
            flash("Please fill out the form!", "danger")
            # Render the form with a success or error message
        return render_template('add_responsibility.html')
    return redirect(url_for('login'))



@app.route('/responsibility', methods=['GET'])
def responsibility():
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM responsibilities')
        responsibilities = cursor.fetchall()
        cursor.close()
        return render_template('responsibility.html', responsibility=responsibilities)
    return redirect(url_for('login'))



@app.route('/edit_responsibility/<int:responsibility_id>', methods=['GET', 'POST'])
def edit_responsibility(responsibility_id):
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Handle GET request (Display the form with existing data)
        if request.method == 'GET':
            cursor.execute('SELECT * FROM responsibilities WHERE id = %s', (responsibility_id,))
            responsibility = cursor.fetchone()
            if not responsibility:
                flash("Responsibility not found!", "danger")
                return redirect(url_for('responsibility', responsibility=responsibility))
            return render_template('edit_responsibility.html', responsibility=responsibility)


        # Handle POST request (Update the responsibility in the database)
        if request.method == 'POST':
            responsibility_name = request.form['responsibility']
            responsibility_description = request.form['description']
            responsibility_path = request.form['path']

            if not responsibility_name or not responsibility_description or not responsibility_path:
                flash("Please fill in all fields!", "danger")
                return redirect(url_for('edit_responsibility', responsibility_id=responsibility_id))

            cursor.execute('UPDATE responsibilities SET name = %s, description = %s, path = %s WHERE id = %s',
                        (responsibility_name, responsibility_description, responsibility_path, responsibility_id))
            mysql.connection.commit()
            cursor.close()
            flash("Responsibility updated successfully!", "success")
            return redirect(url_for('responsibility'))
    return redirect(url_for('login'))



@app.route('/responsibility_delete/<int:responsibility_id>', methods=['GET'])
def responsibility_delete(responsibility_id):
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # First, delete entries from the roles_responsibilities table
        cursor.execute("DELETE FROM roles_responsibilities WHERE responsibility_id = %s", (responsibility_id,))
        cursor.execute("DELETE FROM responsibilities WHERE id = %s", (responsibility_id,))
        mysql.connection.commit()
        flash("Responsibility Deleted Sucessfully!", "danger")
        return redirect(url_for('responsibility'))
    return redirect(url_for('login'))


# Add Book Route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    
    if 'loggedin' in session:  # Ensure the user is logged in
        if request.method == 'POST' and 'title' in request.form and 'author' in request.form and 'quantity' in request.form:
            title = request.form['title']
            author = request.form['author']
            rack = request.form['rack']
            quantity = request.form['quantity']

            text_input = f"{title} {author}"
            embedding = generate_embeddings(text_input)

            # Convert the embedding list to JSON (an array in JSON format)
            embedding_json = json.dumps(embedding)


            # Handle file upload
            image_file = request.files['image']
            if image_file and image_file.filename != '':
                # Ensure the filename is secure and save it
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                image_url = url_for('static', filename='uploads/' + filename)
            else:
                image_url = None  # No image provided

            # Insert book data into the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO add_book (title, author, rack, quantity, image_url, embedding) VALUES (%s, %s, %s, %s, %s, %s)',
                           (title, author, rack, quantity, image_url, embedding_json))
            mysql.connection.commit()
            # Get the ID of the newly inserted user
            new_user_id = cursor.lastrowid

            # Create user_code as 'BK' + new_user_id
            user_code = f'BK{new_user_id}'

            # Update the user_code column with the generated code
            cursor.execute('UPDATE add_book SET isbn = %s WHERE id = %s', (user_code, new_user_id))

            # Commit the update
            mysql.connection.commit()
            flash("Book added successfully!", "success")
            return render_template('add_book.html')
        elif request.method == 'POST':
            flash("Please fill out this form!", "danger")
            return render_template('add_book.html')
        else:
            return render_template('add_book.html')
    return redirect(url_for('login'))


def generate_embeddings(text_input):
    if not isinstance(text_input, str):
        raise ValueError("Expected a string for text_input, got a non-string type.")

    response = openai.Embedding.create(input=text_input, model="text-embedding-ada-002")
    return response['data'][0]['embedding']


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
            flash("Book updated successfully!", "success")
            return redirect(url_for('view_books'))

        # Fetch the book details for the given ID
        cursor.execute('SELECT * FROM add_book WHERE id = %s', (id,))
        book = cursor.fetchone()

        return render_template('edit_book.html', book=book)
    return redirect(url_for('login'))


@app.route('/delete_book/<int:id>', methods=['GET'])
def delete_book(id):
    
    if 'loggedin' in session:  # Ensure the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # delete entries from the add_book table
        cursor.execute("DELETE FROM add_book WHERE id = %s", (id,))
        mysql.connection.commit()
        flash("book Deleted Sucessfully!", "danger")
        return redirect(url_for('books'))
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
        cursor.execute('SELECT id, first_name, last_name ,userid FROM user_table')
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
            SELECT u.first_name, bi.id, b.title, bi.issue_date 
            FROM book_issues bi 
            JOIN add_book b ON bi.book_id = b.id
            JOIN user_table u ON bi.user_id = u.id 
            WHERE bi.return_date IS NULL
        ''')
        issued_books = cursor.fetchall()
        return render_template('issued_books.html', issued_books=issued_books)
    return redirect(url_for('login'))


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


def generate_book_summary(title, author, description=""):
    # Define the message format for generating a book summary
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates book summaries."},
        {"role": "user", "content": f"Provide a summary for the following book:\n\nTitle: {title}\nAuthor: {author}\nDescription: {description}\n\nPlease provide a concise overview of the book, focusing on the main themes, plot, and any notable characters."}
    ]

    try:
        # Use the updated ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=messages,
            max_tokens=150,
            temperature=0.5
        )

        # Extract the summary from the response
        summary = response['choices'][0]['message']['content'].strip()
        print(summary)
        return summary

    except Exception as e:
        print("Error generating summary:", e)
        return "Unable to generate summary at this time due to an unexpected error."

@app.route('/book_summary/<int:book_id>', methods=['GET'])
def book_summary(book_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM add_book WHERE id = %s', (book_id,))
    book = cursor.fetchone()  # Fetch the first matching row as a dictionary

    # Check if the book was found
    if not book:
        return "Book not found", 404

    # Generate summary
    summary = generate_book_summary(book['title'], book['author'], book.get('description', ""))
    return jsonify(book=book, summary=summary)

# Call this function when your app starts
if __name__ == '__main__':
    create_schema()
    with app.app_context():
        populate_books_table()
        assign_books_to_users()
    app.run(debug=True)
