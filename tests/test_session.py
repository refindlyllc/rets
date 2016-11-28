import unittest
from rets import Configuration, Session
from unittest.mock import patch


class SessionTester(unittest.TestCase):

    def setUp(self):
        super(SessionTester, self).setUp()
        conf1_7 = Configuration('1.7')
        conf1_7.login_url = 'http://server.rets.com/rets/Login.ashx'
        conf1_7.username = 'retsuser'
        s = Session(configuration=conf1_7)

        with patch('rets.session.Session.client.get') as MockGet:
            with open('tests/example_rets_responses/Login.xml') as f:
                contents = ''.join(f.readlines())
            MockGet.return_value.text = contents
            s.login()

        self.session = s

    def test_login(self):

        expected_capabilities = {
            'GetMetadata': 'http://server.rets.com/rets/GetMetadata.ashx',
            'GetObject': 'http://server.rets.com/rets/GetObject.ashx',
            'Login': 'http://server.rets.com/rets/Login.ashx',
            'Logout': 'http://server.rets.com/rets/Logout.ashx',
            'PostObject': 'http://server.rets.com/rets/PostObject.ashx',
            'Search': 'http://server.rets.com/rets/Search.ashx',
            'Update': 'http://server.rets.com/rets/Update.ashx'
        }

        self.assertEqual(self.session.capabilities, expected_capabilities)

    def test_system_metadata(self):

        with patch('rets.session.Session.client.get') as MockGet:
            with open('tests/example_rets_responses/GetMetadata.xml') as f:
                contents = ''.join(f.readlines())
            MockGet.return_value.text = contents
            sys_metadata = self.session.get_system_metadata()

        self.assertEqual(sys_metadata.version, '1.11.75998')
        self.assertEqual(sys_metadata.system_id, 'MLS-RETS')

    def test_logout(self):

        with patch('rets.session.Session.client.get') as MockGet:
            with open('tests/example_rets_responses/Logout.html') as f:
                contents = ''.join(f.readlines())
            MockGet.return_value.text = contents
            self.assertTrue(self.session.disconnect())
