import unittest
from flask import Flask, url_for
from bs4 import BeautifulSoup

from app import app

class TestAuthTemplates(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_page_load(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        self.assertIsNotNone(soup.find('h2', text='User Login'))
        self.assertIsNotNone(soup.find('input', {'name': 'email'}))
        self.assertIsNotNone(soup.find('input', {'name': 'password'}))
        self.assertIsNotNone(soup.find('button', text='Login'))

    def test_login_form_submission(self):
        response = self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        #self.assertEqual(response.status_code, 200)
        # Add assertions based on expected behavior after login

    def test_register_page_load(self):
        response = self.app.get('/register')
        #self.assertEqual(response.status_code, 200)
        #soup = BeautifulSoup(response.data, 'html.parser')
        #self.assertIsNotNone(soup.find('h2', text='User Registration'))
        #self.assertIsNotNone(soup.find('input', {'name': 'name'}))
        #self.assertIsNotNone(soup.find('input', {'name': 'last_name'}))
        #self.assertIsNotNone(soup.find('input', {'name': 'email'}))
        #self.assertIsNotNone(soup.find('input', {'name': 'password'}))
        #self.assertIsNotNone(soup.find('input', {'name': 'address'}))
        #self.assertIsNotNone(soup.find('button', text='Register'))

    def test_register_form_submission(self):
        response = self.app.post('/register', data={
            'name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'securepassword',
            'address': '123 Test St'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Add assertions based on expected behavior after registration


if __name__ == '__main__':
    unittest.main()