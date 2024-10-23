import unittest
import os
import sys
import pytest

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all the test modules
from tests.frontend_testcases.test_user_templates import TestUserTemplates
from tests.frontend_testcases.test_book_templates import TestBookTemplates
from tests.frontend_testcases.test_common_templates import TestCommonTemplates
from tests.test_app import FlaskAppTests

class PytestTestCase(unittest.TestCase):
    def test_pytest(self):
        # Run pytest and check for failures
        result = pytest.main(['tests/test1_app.py', '-q', '--tb=short', '--disable-warnings'])
        self.assertEqual(result, 0, "Pytest encountered failures.")

if __name__ == '__main__':
    # Create a test suite combining all test cases
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestUserTemplates))
    test_suite.addTest(unittest.makeSuite(TestBookTemplates))
    test_suite.addTest(unittest.makeSuite(TestCommonTemplates))
    test_suite.addTest(unittest.makeSuite(FlaskAppTests))
    test_suite.addTest(unittest.makeSuite(PytestTestCase))
    

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)