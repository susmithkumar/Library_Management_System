import unittest
from app import app
from app import mysql
import json

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        #Setting up.
        self.app = app.test_client()
        self.app.testing = True 

    def test_home_redirect(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_login_page_load(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page_load(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        response = self.app.post('/login', data=dict(
            email='nonexistent@example.com',
            password='wrongpassword'
        ), follow_redirects=True)
        self.assertIn(b'Incorrect email or password!', response.data)

    def test_register_user(self):
        response = self.app.post('/register', data=dict(
            name='Test User',
            password='testpassword',
            email='testuser@example.com',
            address='Test Address',
            last_name='Test'
        ), follow_redirects=True)
        #self.assertIn(b'You have successfully registered!', response.data)

    
    def test_add_book(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['user_id'] = 1
            response = client.post('/add_book', data=dict(
                title='Test Book',
                author='Test Author',
                rack='Test Rack',
                quantity='5'
            ), follow_redirects=True)
            #self.assertIn(b'Book added successfully!', response.data)
    
    def test_search_books(self):
        response = self.app.post('/search_books', data=dict(
            search_term='Test'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()