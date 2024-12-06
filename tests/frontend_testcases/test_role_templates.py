import unittest
from flask_testing import TestCase
from app import app, mysql
from bs4 import BeautifulSoup

class TestRoleTemplates(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})

    """
    def test_roles_template(self):
        response = self.client.get('/roles')
        #self.assert200(response)
        self.assert_template_used('roles.html')

        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for left_menus.html inclusion
        self.assertIsNotNone(soup.find(text=lambda text: '{%' in text and 'include' in text and 'left_menus.html' in text))

        # Check for "All Roles" header
        self.assertIsNotNone(soup.find('h2', string='All Roles'))

        # Check for "Add New Role" link
        self.assertIsNotNone(soup.find('a', string='Add New Role'))

        
        table = soup.find('table')
        if table:
            headers = table.find_all('th')
            expected_headers = ['ID', 'Role Name', 'Description', 'Responsibility', 'Actions']
            self.assertEqual([header.text.strip() for header in headers], expected_headers)

        
        self.assertIsNotNone(soup.find(string='Edit'))
    """

if __name__ == '__main__':
    unittest.main()