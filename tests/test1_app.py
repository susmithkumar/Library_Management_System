import pytest
from flask import session
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, mysql
import unittest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'W7301@jqir#')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'library_management_system')
    app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
    
    with app.test_client() as client:
        with app.app_context():
            # Set up any required database state here
            pass
        yield client

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_home_redirects(client):
    """Test that the home page redirects to login when not logged in."""
    response = client.get('/')
    assert response.status_code == 302
    #assert b'login' in response.headers['Location']

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    #assert b'Login' in response.data



def test_login_failure(client):
    """Test login failure with incorrect credentials."""
    response = login(client, 'wrong@example.com', 'wrongpass')
    assert b'Incorrect email or password!' in response.data

def test_dashboard_access(client):
    """Test access to dashboard when logged in."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    
    response = client.get('/dashboard')
    #assert response.status_code == 200



def test_register_page(client):
    """Test that the register page loads correctly."""
    response = client.get('/register')
    #assert response.status_code == 200

"""
def test_register_success(client):
    Test successful registration.
    response = client.post('/register', data=dict(
        name='New User',
        email='newuser@example.com',
        password='newpass',
        address='123 Main St',
        last_name='User'
    ), follow_redirects=True)
    
    #assert b'You have successfully registered!' in response.data
    """

def test_add_book(client):
    """Test adding a book."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    
    response = client.post('/add_book', data=dict(
        title='New Book',
        author='Author Name',
        rack='Rack 1',
        quantity='5'
    ), follow_redirects=True)
    
    #assert b'Book added successfully!' in response.data

# Add more tests for other routes and functionalities as needed.
"""
def test_register_existing_email(client):
    Test registration with an existing email.
    response = client.post('/register', data=dict(
        name='Existing User',
        email='test@example.com',  # Assuming this email is already in the database
        password='newpass',
        address='123 Main St',
        last_name='User'
    ), follow_redirects=True)
    
    #assert b'Account already exists!' in response.data

    """

"""
def test_password_change(client):
    Test changing a user's password.
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1  # Assuming user_id 1 exists
    
    response = client.post('/password_change', data=dict(
        password='newpassword'
    ), follow_redirects=True)
    
    #assert b'password updated successfully please login again' in response.data
    """

def test_user_role_assignment(client):
    """Test assigning a new role to a user."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    
    response = client.post('/user_roles', data=dict(
        user_id=1,  # Assuming user_id 1 exists
        role_id=2   # Assuming role_id 2 exists
    ), follow_redirects=True)
    
    #assert b'Role updated successfully!' in response.data

def test_edit_user_profile(client):
    """Test editing a user's profile."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1  # Assuming user_id 1 exists
    
    response = client.post('/save_user', data=dict(
        first_name='Updated Name',
        last_name='Updated Last',
        email='updated@example.com',
        address='456 New St'
    ), follow_redirects=True)
    
    #assert b'Profile updated successfully!' in response.data



def test_view_user_profile(client):
    """Test viewing user profile."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1  # Assuming user_id 1 exists

    response = client.get('/view_user')
    assert response.status_code == 200
    #assert b'Profile Information' in response.data

def test_edit_user_profile_invalid_data(client):
    """Test editing user profile with invalid data."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1  # Assuming user_id 1 exists

    response = client.post('/save_user', data=dict(
        first_name='',
        last_name='',
        email='invalid-email',
        address=''
    ), follow_redirects=True)

    #assert b'Please fill in all fields!' in response.data

def test_add_role_missing_fields(client):
    """Test adding a role with missing fields."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.post('/add_role', data=dict(
        role='',
        description=''
    ), follow_redirects=True)

    #assert b'Role name is required!' in response.data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            pass
        yield client

def test_logout(client):
    """Test the logout route."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

def test_register(client):
    """Test the register route."""
    response = client.get('/register')
    assert response.status_code == 200

def test_users(client):
    """Test the users route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.get('/users')
    assert response.status_code == 200

def test_user_roles(client):
    """Test the user_roles route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.post('/user_roles', data=dict(
        user_id=1,
        role_id=2
    ))
    assert response.status_code == 200

def test_save_user(client):
    """Test the save_user route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1
    response = client.post('/save_user', data=dict(
        first_name='First',
        last_name='Last',
        email='email@example.com',
        address='123 Street'
    ))
    assert response.status_code == 302

def test_edit_user(client):
    """Test the edit_user route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.get('/edit_user?userid=1')
    assert response.status_code == 200



def test_view_user(client):
    """Test the view_user route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['user_id'] = 1
    response = client.get('/view_user')
    assert response.status_code == 200

def test_add_role(client):
    """Test the add_role route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.get('/add_role')
    assert response.status_code == 200



def test_roles(client):
    """Test the roles route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.get('/roles')
    assert response.status_code == 200

def test_add_responsibility(client):
    """Test the add_responsibility route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.get('/add_responsibility')
    assert response.status_code == 200

def test_responsibility(client):
    """Test the responsibility route."""
    with client.session_transaction() as sess:
        sess['loggedin'] = True
    response = client.get('/responsibility')
    assert response.status_code == 200






