import unittest
import responses
from rets import models
from rets.session import Session
from rets.exceptions import RETSException


class SessionTester(unittest.TestCase):

    def setUp(self):
        super(SessionTester, self).setUp()
        with open('tests/rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            self.session = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser',
                                   version='1.7.2')
            self.session.login()

    def test_login(self):
        expected_capabilities = {
            u'GetMetadata': u'http://server.rets.com/rets/GetMetadata.ashx',
            u'GetObject': u'http://server.rets.com/rets/GetObject.ashx',
            u'Login': u'http://server.rets.com/rets/Login.ashx',
            u'Logout': u'http://server.rets.com/rets/Logout.ashx',
            u'PostObject': u'http://server.rets.com/rets/PostObject.ashx',
            u'Search': u'http://server.rets.com/rets/Search.ashx',
            u'Update': u'http://server.rets.com/rets/Update.ashx'
        }

        with open('tests/rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with open('tests/rets_responses/Logout.html') as f:
            logout_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Login_no_host.xml') as f:
            no_host_contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            s = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.5')
            s.login()

            self.assertEqual(s.capabilities, expected_capabilities)
            self.assertEquals(s.version, '1.5')

            with self.assertRaises(RETSException):
                Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.99.2')

            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            resps.add(resps.POST, 'http://server.rets.com/rets/Logout.ashx',
                      body=contents, status=200)
            with Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2') as s:
                pass

            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=no_host_contents, status=200, adding_headers={'RETS-Version': 'RETS/1.7.2'})
            s1 = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.5')
            s1.login()
            self.maxDiff = None
            self.assertDictEqual(s1.capabilities, expected_capabilities)
            self.assertEquals(s.version, '1.7.2')

    def test_system_metadata(self):

        with open('tests/rets_responses/GetMetadata_system.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            sys_metadata = self.session.get_system_metadata().pop()

        self.assertEqual(sys_metadata['version'], '1.11.76001')
        self.assertEqual(sys_metadata['system_id'], 'MLS-RETS')

    def test_logout(self):
        with open('tests/rets_responses/Logout.html') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Logout.ashx',
                      body=contents, status=200)

            self.assertTrue(self.session.logout())

    def test_resource_metadata(self):
        with open('tests/rets_responses/GetMetadata_resources.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource = self.session.get_resource_metadata()
            self.assertEqual(len(resource), 6)

    def test_preferred_object(self):
        with open('tests/rets_responses/GetObject.byte') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=contents, status=200, adding_headers={'Content-Type': 'not multipart'})

            obj = self.session.get_preferred_object(resource='Property', r_type='RES', content_id=1)
            self.assertTrue(obj)

            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=contents, status=200, adding_headers={'Content-Type': 'not multipart'})

            resource = {}
            resource['ResourceID'] = 'Agent'
            obj1 = self.session.get_preferred_object(resource=resource, r_type='RES', content_id=1)
            self.assertTrue(obj1)

    def test_class_metadata(self):
        with open('tests/rets_responses/GetMetadata_classes.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource_classes = self.session.get_classes_metadata(resource='Agent')

            self.assertEqual(len(resource_classes), 6)

    def test_search(self):
        with open('tests/rets_responses/GetMetadata_resources.xml') as f:
            resource_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Search.xml') as f:
            search_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Error_InvalidFormat.xml') as f:
            invalid_contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=resource_contents, status=200)
            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search_contents, status=200)
            results = self.session.search(resource='Property',
                                          resource_class='RES',
                                          search_filter={'ListingPrice': 200000})

            self.assertEqual(len(results), 3)
            self.assertEqual(repr(results), '<ResultsSet: 83 Found in Property:RES for (ListingPrice=200000)>')

            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search_contents, status=200)

            results1 = self.session.search(resource='Property',
                                           resource_class='RES',
                                           dmql_query='ListingPrice=200000')
            self.assertEqual(repr(results1), '<ResultsSet: 83 Found in Property:RES for (ListingPrice=200000)>')

            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=invalid_contents, status=200)
            with self.assertRaises(RETSException):
                self.session.search(resource='Property',
                                    resource_class='RES',
                                    dmql_query='ListingPrice=200000',
                                    optional_parameters={'Format': "Somecrazyformat"})

    def test_cache_metadata(self):
        with open('tests/rets_responses/GetMetadata_table.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
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
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            table = self.session.get_table_metadata(resource='Property', resource_class='RES')

        self.assertEqual(len(table), 208)

    def test_lookup_type_metadata(self):
        with open('tests/rets_responses/GetMetadata_lookup.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            lookup_values = self.session.get_lookup_values(resource='Agent', lookup_name='Broker')

        self.assertEqual(len(lookup_values), 61)

    def test_object_metadata(self):
        with open('tests/rets_responses/GetMetadata_objects.xml') as f:
            contents = ''.join(f.readlines())
        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            object_metadata = self.session.get_object_metadata(resource='Agent')

        self.assertEqual(len(object_metadata), 3)

    def test_agent_digest_hash(self):
        self.session.user_agent_password = "testing"
        self.assertIsNotNone(self.session.user_agent_digest_hash())
