import unittest
from rets import parsers
from rets.session import Session
from requests import Response


class TesterWithSession(unittest.TestCase):
    # Provides a valid session object to be provided to the models during testing.
    def setUp(self):
        super(TesterWithSession, self).setUp()
        self.session = Session(login_url='http://rets.com/login.php', username='retsuser', version='1.7.2')


class LookupTypeParserTester(TesterWithSession):

    def test_parse(self):

        with open('tests/rets_responses/GetMetadata_lookup.xml', 'r') as f:
            contents = f.readlines()
            contents = ''.join([c for c in contents])

