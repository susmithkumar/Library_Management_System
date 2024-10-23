import unittest
from bs4 import BeautifulSoup
import os

class TestUserTemplates(unittest.TestCase):

    def setUp(self):
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    """
    def test_view_user_template(self):
        with open(os.path.join(self.templates_dir, 'view_user.html'), 'r') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        self.assertIsNotNone(soup.find('h3', string='User Details'))
        self.assertIsNotNone(soup.find('h4'))
        self.assertIn('Email:', soup.text)
        self.assertIn('Role:', soup.text)
        self.assertIn('Address:', soup.text)
        self.assertIn('Active:', soup.text)
        self.assertIn('Userid:', soup.text)

        # Check for at least one 'Edit Profile' string
        self.assertGreaterEqual(len(soup.find_all(string='Edit Profile')), 1)

    
    def test_users_template(self):
        with open(os.path.join(self.templates_dir, 'users.html'), 'r') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        self.assertIsNotNone(soup.find(string='User Listing'))
        table = soup.find('table')
        self.assertIsNotNone(table)
        
        # Check table headers
        headers = [th.text.strip() for th in table.find_all('th')]
        self.assertEqual(headers, ['Name', 'Role'])
        
        # Check table data
        data_row = table.find('tr', recursive=False)
        self.assertIsNotNone(data_row)
        cells = data_row.find_all('td')
        
        # Check for user data placeholders and actions
        expected_contents = ['{{user.first_name}}', '{{user.email}}', '{{user.role}}', 'View', 'Edit', 'Change Password', 'Delete']
        cell_contents = [cell.text.strip() for cell in cells]
        for expected in expected_contents:
            self.assertIn(expected, cell_contents)
    """

if __name__ == '__main__':
    unittest.main()