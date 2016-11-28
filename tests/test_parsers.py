import unittest
from rets import parsers
from rets.configuration import Configuration
from rets.session import Session
from requests import Response


class TesterWithSession(unittest.TestCase):
    # Provides a valid session object to be provided to the models during testing.
    def setUp(self):
        super(TesterWithSession, self).setUp()
        c = Configuration('1.7.2')
        c.login_url = 'http://rets.com/login.php'
        c.username = 'retsuser'
        self.session = Session(c)


class LookupTypeParserTester(TesterWithSession):

    def test_parse(self):

        with open('tests/example_rets_responses/lookup.xml', 'r') as f:
            contents = f.readlines()
            contents = ''.join([c for c in contents])

