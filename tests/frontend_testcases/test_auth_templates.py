import unittest
from flask_testing import TestCase
from app import app, mysql
from bs4 import BeautifulSoup

class TestAuthTemplates(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    """
    def test_login_template(self):
        response = self.client.get('/login')
        self.assert200(response)
        self.assert_template_used('templates/login.html')

        soup = BeautifulSoup(response.data, 'html.parser')
        form = soup.find('form')
        self.assertIsNotNone(form)
        self.assertEqual(form.get('action'), '/login')
        self.assertEqual(form.get('method'), 'post')

        self.assertIsNotNone(form.find('input', {'name': 'email'}))
        self.assertIsNotNone(form.find('input', {'name': 'password'}))
        self.assertIsNotNone(form.find('button', {'type': 'submit'}))

        self.assertIsNotNone(soup.find('a', href='/register'))

    def test_register_template(self):
        response = self.client.get('/register')
        self.assert200(response)
        self.assert_template_used('templates/register.html')

        soup = BeautifulSoup(response.data, 'html.parser')
        form = soup.find('form')
        self.assertIsNotNone(form)
        self.assertEqual(form.get('action'), '/register')
        self.assertEqual(form.get('method'), 'post')
        self.assertIsNotNone(form.find('input', {'name': 'name'}))
        self.assertIsNotNone(form.find('input', {'name': 'email'}))
        self.assertIsNotNone(form.find('input', {'name': 'password'}))
        self.assertIsNotNone(form.find('button', {'type': 'submit'}))

        self.assertIsNotNone(soup.find('a', href='/login'))
    """

if __name__ == '__main__':
    unittest.main()