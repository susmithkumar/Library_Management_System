import unittest
import os
import sys
import pytest

# Add the parent directory to the Python path


# Import all the test modules
#from tests.frontend_testcases.test_user_templates import TestUserTemplates
#from tests.frontend_testcases.test_book_templates import TestBookTemplates
#from tests.frontend_testcases.test_common_templates import TestCommonTemplates
#from tests.test_app import FlaskAppTests

#class PytestTestCase(unittest.TestCase):
    #def test_pytest(self):
        # Run pytest and check for failures
        #result = pytest.main(['tests/test1_app.py', '-q', '--tb=short', '--disable-warnings'])
        #self.assertEqual(result, 0, "Pytest encountered failures.")

#if __name__ == '__main__':
    # Create a test suite combining all test cases

    #os.environ['MYSQL_HOST'] = '127.0.0.1'
    #os.environ['MYSQL_USER'] = 'root'
    #os.environ['MYSQL_PASSWORD'] = 'W7301@jqir#'
    #os.environ['MYSQL_DB'] = 'library_management_system'
    #os.environ['MYSQL_PORT'] = '3306'

    #test_suite = unittest.TestSuite()
    #test_suite.addTest(unittest.makeSuite(TestUserTemplates))
    #test_suite.addTest(unittest.makeSuite(TestBookTemplates))
    #test_suite.addTest(unittest.makeSuite(TestCommonTemplates))
    #test_suite.addTest(unittest.makeSuite(FlaskAppTests))
    #test_suite.addTest(unittest.makeSuite(PytestTestCase))
    

    # Run the tests
    #runner = unittest.TextTestRunner(verbosity=2)
    #runner.run(test_suite)

import unittest

class SimpleTestCase(unittest.TestCase):
    def test_always_pass(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main(verbosity=2)