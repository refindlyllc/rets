import unittest
import responses
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
            sys_metadata = self.session.get_system_metadata()

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

    def test_get_object(self):

        with open('tests/rets_responses/GetObject.byte', 'rb') as f:
            single = f.read()

        with open('tests/rets_responses/GetObject_multipart.byte', 'rb') as f:
            multiple = f.read()

        multi_headers = {'Content-Type': 'multipart/parallel; boundary="24cbd0e0afd2589bb9dcb1f34cf19862"; charset=utf-8',
                         'Connection': 'keep-alive', 'RETS-Version': 'RETS/1.7.2',  'MIME-Version': '1.0, 1.0'}

        single_headers = {'MIME-Version': '1.0, 1.0', 'Object-ID': '0', 'Content-ID': '2144466',
                          'Content-Type': 'image/jpeg', 'Connection': 'keep-alive',
                          'RETS-Version': 'RETS/1.7.2'}

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=single, status=200, adding_headers=single_headers)

            objs = self.session.get_object(resource='Property', object_type='Photo', content_ids='1', object_ids='1')
            self.assertEqual(len(objs), 1)

            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=multiple, status=200, adding_headers=multi_headers)

            objs1 = self.session.get_object(resource='Property', object_type='Photo', content_ids='1')
            self.assertEqual(len(objs1), 9)

    def test_preferred_object(self):
        with open('tests/rets_responses/GetObject_multipart.byte', 'rb') as f:
            multiple = f.read()

        multi_headers = {
            'Content-Type': 'multipart/parallel; boundary="24cbd0e0afd2589bb9dcb1f34cf19862"; charset=utf-8',
            'Connection': 'keep-alive', 'RETS-Version': 'RETS/1.7.2', 'MIME-Version': '1.0, 1.0'}

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=multiple, status=200, adding_headers=multi_headers)

            obj = self.session.get_preferred_object(resource='Property', object_type='Photo', content_id=1)
            self.assertTrue(obj)

            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=multiple, status=200)

            resource = dict()
            resource['ResourceID'] = 'Agent'
            obj1 = self.session.get_preferred_object(resource=resource, object_type='Photo', content_id=1)
            self.assertTrue(obj1)

    def test_class_metadata(self):
        with open('tests/rets_responses/GetMetadata_classes.xml') as f:
            contents = ''.join(f.readlines())

        with open('tests/rets_responses/GetMetadata_classes_single.xml') as f:
            single_contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource_classes = self.session.get_class_metadata(resource='Agent')
            self.assertEqual(len(resource_classes), 6)

            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=single_contents, status=200)
            resource_classes_single = self.session.get_class_metadata(resource='Property')
            self.assertEqual(len(resource_classes_single), 1)

    def test_search(self):
        with open('tests/rets_responses/GetMetadata_resources.xml') as f:
            resource_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Search.xml') as f:
            search_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Search_1of2.xml') as f:
            search1_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Search_2of2.xml') as f:
            search2_contents = ''.join(f.readlines())

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

            self.assertEqual(results.results_count, 3)
            self.assertEqual(repr(results), '<ResultsSet: 3 Found in Property:RES for (ListingPrice=200000)>')

            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search_contents, status=200)

            results1 = self.session.search(resource='Property',
                                           resource_class='RES',
                                           limit=3,
                                           dmql_query='ListingPrice=200000',
                                           optional_parameters={'RestrictedIndicator': '!!!!'})
            self.assertEqual(repr(results1), '<ResultsSet: 3 Found in Property:RES for (ListingPrice=200000)>')

            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=invalid_contents, status=200)
            with self.assertRaises(RETSException):
                self.session.search(resource='Property',
                                    resource_class='RES',
                                    dmql_query='ListingPrice=200000',
                                    optional_parameters={'Format': "Somecrazyformat"})

            # Test multiple calls with offset
            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search1_contents, status=200)
            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search2_contents, status=200)
            results2 = self.session.search(resource='Property',
                                           resource_class='RES',
                                           dmql_query='ListingPrice=200000')
            self.assertEqual(6, results2.results_count)
            self.assertEqual(repr(results2), '<ResultsSet: 6 Found in Property:RES for (ListingPrice=200000)>')

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
        self.assertIsNotNone(self.session._user_agent_digest_hash())
