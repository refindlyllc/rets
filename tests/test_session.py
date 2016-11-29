import unittest
import responses
import re
from rets.session import Session
from rets.exceptions import MetadataNotFound


class SessionTester(unittest.TestCase):

    def setUp(self):
        super(SessionTester, self).setUp()
        self.session = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2')

        with open('tests/example_rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            self.session.login()

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

        s = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2')
        with open('tests/example_rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            s.login()

        self.assertEqual(s.capabilities, expected_capabilities)

        s1 = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2')
        with open('tests/example_rets_responses/Login_no_host.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            s1.login()

        self.assertEqual(s1.capabilities, expected_capabilities)

    def test_system_metadata(self):

        with open('tests/example_rets_responses/GetMetadata.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            sys_metadata = self.session.get_system_metadata()

        self.assertEqual(sys_metadata.version, '1.11.75998')
        self.assertEqual(sys_metadata.system_id, 'MLS-RETS')

    def test_logout(self):
        with open('tests/example_rets_responses/Logout.html') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Logout.ashx',
                      body=contents, status=200)

            self.assertTrue(self.session.disconnect())

    @unittest.skip('until i can figure this out')
    def test_resource_metadata(self):
        with open('tests/example_rets_responses/resources.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock(assert_all_requests_are_fired=True) as resps:
            url_re = re.compile(pattern=r'http://server\.rets\.com/rets/GetMetadata\.ashx.+')
            resps.add(resps.GET, url_re,
                      body=contents, status=200)
            resource = self.session.get_resources_metadata(resource_id='Agent')

            self.assertEqual(resource.ResourceID, 'Agent')

            with self.assertRaises(MetadataNotFound):
                self.session.get_resources_metadata(resource_id='NotReal')

    def test_preferred_object(self):
        with open('tests/example_rets_responses/GetObject.byte') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            url_re = re.compile(pattern=r'http://server\.rets\.com/rets/GetObject\.ashx.+')
            resps.add(resps.GET, url_re,
                      body=contents, status=200, adding_headers={'Content-Type': 'not multipart'})

            obj = self.session.get_preferred_object(resource='Property', r_type='RES', content_id=1)
        self.assertTrue(obj)

    def test_agent_digest_hash(self):
        self.session.user_agent_password = "testing"
        self.assertIsNotNone(self.session.user_agent_digest_hash())
