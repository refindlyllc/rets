import unittest
import responses
import re
from rets.session import Session
from rets.exceptions import MetadataNotFound


class SessionTester(unittest.TestCase):

    def setUp(self):
        super(SessionTester, self).setUp()
        self.session = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2')

        with open('tests/rets_responses/Login.xml') as f:
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
        with open('tests/rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            s.login()

        self.assertEqual(s.capabilities, expected_capabilities)

        s1 = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2')
        with open('tests/rets_responses/Login_no_host.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            s1.login()

        self.assertEqual(s1.capabilities, expected_capabilities)

    def test_system_metadata(self):

        with open('tests/rets_responses/GetMetadata_system.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            sys_metadata = self.session.get_system_metadata()

        self.assertEqual(sys_metadata.version, '1.11.75998')
        self.assertEqual(sys_metadata.system_id, 'MLS-RETS')

    def test_logout(self):
        with open('tests/rets_responses/Logout.html') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/Logout.ashx',
                      body=contents, status=200)

            self.assertTrue(self.session.disconnect())

    def test_resource_metadata(self):
        with open('tests/rets_responses/GetMetadata_resources.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource = self.session.get_resource_metadata(resource='Agent')

            self.assertEqual(resource.ResourceID, 'Agent')

            with self.assertRaises(MetadataNotFound):
                self.session.get_resource_metadata(resource='NotReal')

    def test_preferred_object(self):
        with open('tests/rets_responses/GetObject.byte') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetObject.ashx',
                      body=contents, status=200, adding_headers={'Content-Type': 'not multipart'})

            obj = self.session.get_preferred_object(resource='Property', r_type='RES', content_id=1)
        self.assertTrue(obj)

    def test_class_metadata(self):
        with open('tests/rets_responses/GetMetadata_classes.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource_classes = self.session.get_classes_metadata(resource='Agent')

            self.assertEqual(resource_classes['RES'].Description, 'Residential')

    def test_search(self):
        with open('tests/rets_responses/GetMetadata_resources.xml') as f:
            resource_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Search.xml') as f:
            search_contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=resource_contents, status=200)
            resps.add(resps.GET, 'http://server.rets.com/rets/Search.ashx',
                      body=search_contents, status=200)
            results = self.session.search(resource_id='Property',
                                          class_id='RES',
                                          search_filter={'ListingPrice': 200000})

            self.assertEqual(len(results), 3)
            self.assertEqual(repr(results), '<Results: 83 Found in Property:RES for (ListingPrice=200000)>')

    def test_cache_metadata(self):
        with open('tests/rets_responses/GetMetadata_table.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            t1 = self.session.get_table_metadata(resource='Property', resource_class='RES')

        self.assertIn('METADATA-TABLE:Property:RES', list(self.session.metadata_responses.keys()))

        # Subsequent call without RequestMock should fail unless we get the saved response from metadata_responses
        table = self.session.get_table_metadata(resource='Property', resource_class='RES')
        self.assertEqual(len(table), 208)

    def test_table_metadata(self):
        with open('tests/rets_responses/GetMetadata_table.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            table = self.session.get_table_metadata(resource='Property', resource_class='RES')

        self.assertEqual(len(table), 208)

    def test_lookup_type_metadata(self):
        with open('tests/rets_responses/GetMetadata_lookup.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            lookup_values = self.session.get_lookup_values(resource='Agent', lookup_name='Broker')

        self.assertEqual(len(lookup_values), 61)

    def test_object_metadata(self):
        with open('tests/rets_responses/GetMetadata_objects.xml') as f:
            contents = ''.join(f.readlines())
        with responses.RequestsMock() as resps:
            resps.add(resps.GET, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            object_metadata = self.session.get_object_metadata(resource='Agent')

        self.assertEqual(len(object_metadata), 3)

    def test_agent_digest_hash(self):
        self.session.user_agent_password = "testing"
        self.assertIsNotNone(self.session.user_agent_digest_hash())
