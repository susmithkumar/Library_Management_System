import unittest
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all the test modules
from frontend_testcases.test_user_templates import TestUserTemplates
from frontend_testcases.test_book_templates import TestBookTemplates
from frontend_testcases.test_common_templates import TestCommonTemplates

if __name__ == '__main__':
    # Create a test suite combining all test cases
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestUserTemplates))
    test_suite.addTest(unittest.makeSuite(TestBookTemplates))
    test_suite.addTest(unittest.makeSuite(TestCommonTemplates))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)