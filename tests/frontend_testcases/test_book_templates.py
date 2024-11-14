import unittest
from bs4 import BeautifulSoup
import os

class TestBookTemplates(unittest.TestCase):

    def setUp(self):
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

    def test_view_books_template(self):
        with open(os.path.join(self.templates_dir, 'view_books.html'), 'r') as file:
            content = file.read()

        soup = BeautifulSoup(content, 'html.parser')

        self.assertIsNotNone(soup.find('h2', string='View All Books'))
        table = soup.find('table')
        self.assertIsNotNone(table)
        headers = [th.text.strip() for th in table.find_all('th')]
        expected_headers = ['ID', 'Title', 'Author', 'Rack', 'Quantity', 'ISBN']
        self.assertEqual(headers, expected_headers)

        #self.assertIsNotNone(soup.find(string='Edit'))

if __name__ == '__main__':
    unittest.main()