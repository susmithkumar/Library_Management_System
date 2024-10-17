import unittest
from bs4 import BeautifulSoup
import os

class TestCommonTemplates(unittest.TestCase):

    def setUp(self):
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

    def test_left_menus_template(self):
        with open(os.path.join(self.templates_dir, 'left_menus.html'), 'r') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        

if __name__ == '__main__':
    unittest.main()