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

    def test_system_metadata(self):

        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_system.xml') as f:
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
        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_resources.xml') as f:
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
            self.assertEqual(objs[0]['content_md5'], '396106a133a23e10f6926a82d219edbc')

            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=multiple, status=200, adding_headers=multi_headers)

            objs1 = self.session.get_object(resource='Property', object_type='Photo', content_ids='1')
            self.assertEqual(len(objs1), 9)

    def test_get_object_location1(self):
        with open('tests/rets_responses/GetObject_multipart_Location1.byte', 'rb') as f:
            multiple = f.read()

        multi_headers = {
            'Content-Type': 'multipart/parallel; boundary="FLEXLIAsmcpmiKpZ3uhewHnpQUlQNYzuNzPeUi0PIqCAxzgSRkpypX"; charset=utf-8',
            'Connection': 'keep-alive', 'RETS-Version': 'RETS/1.7.2', 'MIME-Version': '1.0, 1.0'}

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetObject.ashx',
                      body=multiple, status=200, adding_headers=multi_headers)

            objs1 = self.session.get_object(resource='Property', object_type='Photo', content_ids='1', location='1')
            self.assertEqual(len(objs1), 41)

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
        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_classes.xml') as f:
            contents = ''.join(f.readlines())

        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_classes_single.xml') as f:
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

        with open('tests/rets_responses/COMPACT-DECODED/Search.xml') as f:
            search_contents = ''.join(f.readlines())

        with open('tests/rets_responses/COMPACT-DECODED/Search_1of2.xml') as f:
            search1_contents = ''.join(f.readlines())

        with open('tests/rets_responses/COMPACT-DECODED/Search_2of2.xml') as f:
            search2_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Errors/Error_InvalidFormat.xml') as f:
            invalid_contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search_contents, status=200, stream=True)
            results = self.session.search(resource='Property',
                                          resource_class='RES',
                                          search_filter={'ListingPrice': 200000})

            self.assertEqual(len(list(results)), 3)

            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=search_contents, status=200, stream=True)

            results1 = self.session.search(resource='Property',
                                           resource_class='RES',
                                           limit=3,
                                           dmql_query='ListingPrice=200000',
                                           optional_parameters={'RestrictedIndicator': '!!!!'})
            results1_ls = list(results1)
            self.assertEqual(len(results1_ls), 3)

            resps.add(resps.POST, 'http://server.rets.com/rets/Search.ashx',
                      body=invalid_contents, status=200, stream=True)
            with self.assertRaises(RETSException):
                res = self.session.search(resource='Property',
                                          resource_class='RES',
                                          dmql_query='ListingPrice=200000',
                                          optional_parameters={'Format': "Somecrazyformat"})
                for r in res:
                    pass  # initiating the generator

    def test_cache_metadata(self):
        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_table.xml') as f:
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
        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_table.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            table = self.session.get_table_metadata(resource='Property', resource_class='RES')

        self.assertEqual(len(table), 208)

    def test_lookup_type_metadata(self):
        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_lookup.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            lookup_values = self.session.get_lookup_values(resource='Agent', lookup_name='Broker')

        self.assertEqual(len(lookup_values), 61)

    def test_object_metadata(self):
        with open('tests/rets_responses/COMPACT-DECODED/GetMetadata_objects.xml') as f:
            contents = ''.join(f.readlines())
        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            object_metadata = self.session.get_object_metadata(resource='Agent')

        self.assertEqual(len(object_metadata), 3)

    def test_agent_digest_hash(self):
        self.session.user_agent_password = "testing"
        self.assertIsNotNone(self.session._user_agent_digest_hash())

    def test_change_parser_automatically(self):
        self.assertEqual(self.session.metadata_format, 'COMPACT-DECODED')

        with open('tests/rets_responses/Errors/20514.xml') as f:
            dtd_error = ''.join(f.readlines())

        with open('tests/rets_responses/STANDARD-XML/GetMetadata_system.xml') as f:
            content = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=dtd_error, status=200)
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=content, status=200)
            self.session.get_system_metadata()

        self.assertEqual(self.session.metadata_format, 'STANDARD-XML')


class Session15Tester(unittest.TestCase):
    def setUp(self):
        super(Session15Tester, self).setUp()
        with open('tests/rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            self.session = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser',
                                   version='1.5')
            self.session.metadata_format = 'STANDARD-XML'
            self.session.login()

    def test_system_metadata(self):
        with open('tests/rets_responses/STANDARD-XML/GetMetadata_system.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            sys_metadata = self.session.get_system_metadata()

        self.assertEqual(sys_metadata['version'], '45.61.69081')
        self.assertEqual(sys_metadata['system_id'], 'RETS')

    def test_resource_metadata(self):
        with open('tests/rets_responses/STANDARD-XML/GetMetadata_resources.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource = self.session.get_resource_metadata()
            self.assertEqual(len(resource), 2)

    def test_class_metadata(self):
        with open('tests/rets_responses/STANDARD-XML/GetMetadata_classes.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            resource_classes = self.session.get_class_metadata(resource='Agent')
            self.assertEqual(len(resource_classes), 8)

    def test_table_metadata(self):
        with open('tests/rets_responses/STANDARD-XML/GetMetadata_table.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            table = self.session.get_table_metadata(resource='Property', resource_class='1')

        self.assertEqual(len(table), 162)

    def test_lookup_type_metadata(self):
        with open('tests/rets_responses/STANDARD-XML/GetMetadata_lookup.xml') as f:
            contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            lookup_values = self.session.get_lookup_values(resource='Property', lookup_name='1_2')

        self.assertEqual(len(lookup_values), 9)

    def test_object_metadata(self):
        with open('tests/rets_responses/STANDARD-XML/GetMetadata_objects.xml') as f:
            contents = ''.join(f.readlines())
        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/GetMetadata.ashx',
                      body=contents, status=200)
            object_metadata = self.session.get_object_metadata(resource='Agent')

        self.assertEqual(len(object_metadata), 1)


class LoginTester(unittest.TestCase):
    def test_login(self):
        expected_capabilities1 = {
            u'GetMetadata': u'http://server.rets.com/rets/GetMetadata.ashx',
            u'GetObject': u'http://server.rets.com/rets/GetObject.ashx',
            u'Login': u'http://server.rets.com/rets/Login.ashx',
            u'Logout': u'http://server.rets.com/rets/Logout.ashx',
            u'PostObject': u'http://server.rets.com/rets/PostObject.ashx',
            u'Search': u'http://server.rets.com/rets/Search.ashx',
            u'Update': u'http://server.rets.com/rets/Update.ashx'
        }

        expected_capabilities2 = {
            u'GetMetadata': u'http://server.rets.com/rets/GetMetadata.ashx',
            u'GetObject': u'http://server.rets.com/rets/GetObject.ashx',
            u'Login': u'http://server.rets.com/rets/Login.ashx',
            u'Logout': u'http://server.rets.com/rets/Logout.ashx',
            u'Search': u'http://server.rets.com/rets/Search.ashx',
        }

        with open('tests/rets_responses/Login.xml') as f:
            contents = ''.join(f.readlines())

        with open('tests/rets_responses/Logout.html') as f:
            logout_contents = ''.join(f.readlines())

        with open('tests/rets_responses/Errors/Login_no_host.xml') as f:
            no_host_contents = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            s = Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.5')
            s.login()

            self.assertEqual(s.capabilities, expected_capabilities1)
            self.assertEquals(s.version, '1.5')

            resps.add(resps.POST, 'http://server.rets.com/rets/Login.ashx',
                      body=contents, status=200)
            resps.add(resps.POST, 'http://server.rets.com/rets/Logout.ashx',
                      body=logout_contents, status=200)
            with Session(login_url='http://server.rets.com/rets/Login.ashx', username='retsuser', version='1.7.2') as s:
                pass

            resps.add(resps.POST, 'http://server.rets.com/rets/Login_no_host.ashx',
                      body=no_host_contents, status=200, adding_headers={'RETS-Version': 'RETS/1.7.2'})
            s1 = Session(login_url='http://server.rets.com/rets/Login_no_host.ashx', username='retsuser', version='1.5')
            s1.login()

            self.assertDictEqual(s1.capabilities, expected_capabilities2)
            self.assertEquals(s.version, '1.7.2')

    def test_login_with_action(self):
        with open('tests/rets_responses/Login_with_Action.xml') as f:
            action_login = ''.join(f.readlines())

        with open('tests/rets_responses/Action.xml') as f:
            action_response = ''.join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(resps.POST, 'http://server.rets.com/rets/Login_with_Action.ashx',
                      body=action_login, status=200)
            resps.add(resps.GET, 'http://server.rets.com/rets/Action.ashx',
                      body=action_response, status=200)

            s2 = Session(login_url='http://server.rets.com/rets/Login_with_Action.ashx', username='retsuser',
                         version='1.5')
            s2.login()
            self.assertIn(u'Action', s2.capabilities.keys())
