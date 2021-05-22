import unittest

import responses
from tests.custom_parser_example import CreaStandardXParser
from six.moves.urllib.parse import urlparse

from rets.exceptions import RETSException
from rets.session import Session


class SessionTester(unittest.TestCase):
    def setUp(self):
        super(SessionTester, self).setUp()
        with open("tests/rets_responses/Login.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Login.ashx",
                body=contents,
                status=200,
                headers={"Set-Cookie": "ASP.NET_SessionId=zacqcc1gjhkmazjznjmyrinq;"},
            )
            self.session = Session(
                login_url="http://server.rets.com/rets/Login.ashx",
                username="retsuser",
                version="RETS/1.7.2",
                session_id_cookie_name="ASP.NET_SessionId",
            )
            self.session.login()

    def test_system_metadata(self):

        with open("tests/rets_responses/COMPACT-DECODED/GetMetadata_system.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            sys_metadata = self.session.get_system_metadata()

        self.assertEqual(sys_metadata["version"], "1.11.76001")
        self.assertEqual(sys_metadata["system_id"], "MLS-RETS")

    def test_logout(self):
        with open("tests/rets_responses/Logout.html") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Logout.ashx",
                body=contents,
                status=200,
            )

            self.assertTrue(self.session.logout())

    def test_resource_metadata(self):
        with open(
            "tests/rets_responses/COMPACT-DECODED/GetMetadata_resources.xml"
        ) as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            resource = self.session.get_resource_metadata()
            self.assertEqual(len(list(resource)), 6)

    def test_get_object(self):

        with open("tests/rets_responses/GetObject.byte", "rb") as f:
            single = f.read()

        with open("tests/rets_responses/GetObject_multipart.byte", "rb") as f:
            multiple = f.read()

        multi_headers = {
            "Content-Type": 'multipart/parallel; boundary="24cbd0e0afd2589bb9dcb1f34cf19862"; charset=utf-8',
            "Connection": "keep-alive",
            "RETS-Version": "RETS/1.7.2",
            "MIME-Version": "1.0, 1.0",
        }

        single_headers = {
            "MIME-Version": "1.0, 1.0",
            "Object-ID": "0",
            "Content-ID": "2144466",
            "Content-Type": "image/jpeg",
            "Connection": "keep-alive",
            "RETS-Version": "RETS/1.7.2",
        }

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetObject.ashx",
                body=single,
                status=200,
                headers=single_headers,
            )

            objs = self.session.get_object(
                resource="Property",
                object_type="Photo",
                content_ids="1",
                object_ids="1",
            )
            obj_l = list(objs)
            self.assertEqual(len(obj_l), 1)
            self.assertEqual(obj_l[0]["content_md5"], "396106a133a23e10f6926a82d219edbc")

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetObject.ashx",
                body=multiple,
                status=200,
                headers=multi_headers,
            )

            objs1 = self.session.get_object(
                resource="Property", object_type="Photo", content_ids="1"
            )
            self.assertEqual(len(list(objs1)), 9)

    def test_get_object_location1(self):
        with open("tests/rets_responses/GetObject_multipart_Location1.byte", "rb") as f:
            multiple = f.read()

        multi_headers = {
            "Content-Type": "multipart/parallel; "
            'boundary="FLEXLIAsmcpmiKpZ3uhewHnpQUlQNYzuNzPeUi0PIqCAxzgSRkpypX"; '
            "charset=utf-8",
            "Connection": "keep-alive",
            "RETS-Version": "RETS/1.7.2",
            "MIME-Version": "1.0, 1.0",
        }

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetObject.ashx",
                body=multiple,
                status=200,
                headers=multi_headers,
            )

            objs1 = self.session.get_object(
                resource="Property", object_type="Photo", content_ids="1", location="1"
            )
            self.assertEqual(len(list(objs1)), 41)

    def test_preferred_object(self):
        with open("tests/rets_responses/GetObject_multipart.byte", "rb") as f:
            multiple = f.read()

        multi_headers = {
            "Content-Type": 'multipart/parallel; boundary="24cbd0e0afd2589bb9dcb1f34cf19862"; charset=utf-8',
            "Connection": "keep-alive",
            "RETS-Version": "RETS/1.7.2",
            "MIME-Version": "1.0, 1.0",
        }

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetObject.ashx",
                body=multiple,
                status=200,
                headers=multi_headers,
            )

            obj = self.session.get_preferred_object(
                resource="Property", object_type="Photo", content_id=1
            )
            self.assertTrue(obj)

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetObject.ashx",
                body=multiple,
                status=200,
            )

            resource = dict()
            resource["ResourceID"] = "Agent"
            obj1 = self.session.get_preferred_object(
                resource=resource, object_type="Photo", content_id=1
            )
            self.assertTrue(obj1)

    def test_class_metadata(self):
        with open("tests/rets_responses/COMPACT-DECODED/GetMetadata_classes.xml") as f:
            contents = "".join(f.readlines())

        with open(
            "tests/rets_responses/COMPACT-DECODED/GetMetadata_classes_single.xml"
        ) as f:
            single_contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            resource_classes = self.session.get_class_metadata(resource="Agent")
            self.assertEqual(len(list(resource_classes)), 6)

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=single_contents,
                status=200,
            )
            resource_classes_single = self.session.get_class_metadata(
                resource="Property"
            )
            self.assertEqual(len(list(resource_classes_single)), 1)

    def test_search(self):

        with open("tests/rets_responses/COMPACT-DECODED/Search.xml") as f:
            search_contents = "".join(f.readlines())

        with open("tests/rets_responses/CREA-STANDARD-XML/Search.xml") as f:
            custom_search_contents = "".join(f.readlines())

        with open("tests/rets_responses/Errors/Error_InvalidFormat.xml") as f:
            invalid_contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Search.ashx",
                body=search_contents,
                status=200,
                stream=True,
            )
            results_gen = self.session.search(
                resource="Property",
                resource_class="RES",
                search_filter={"ListingPrice": 200000},
            )
            results = list(results_gen)
            self.assertEqual(len(results), 3)

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Search.ashx",
                body=search_contents,
                status=200,
                stream=True,
            )

            results1_gen = self.session.search(
                resource="Property",
                resource_class="RES",
                limit=3,
                dmql_query="ListingPrice=200000",
                optional_parameters={"RestrictedIndicator": "!!!!"},
            )
            results1 = list(results1_gen)
            self.assertEqual(len(results1), 3)

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Search.ashx",
                body=custom_search_contents,
                status=200,
                stream=True,
            )

            self.session.search_parser = CreaStandardXParser()
            results2_gen = self.session.search(
                resource="Property",
                resource_class="Property",
                limit=1,
                response_format="STANDARD-XML",
                dmql_query="(ID=20270724)",
            )
            results2 = list(results2_gen)
            self.assertEqual(len(results2), 1)
            self.session.search_parser = None

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Search.ashx",
                body=invalid_contents,
                status=200,
                stream=True,
            )
            with self.assertRaises(RETSException):
                r = self.session.search(
                    resource="Property",
                    resource_class="RES",
                    dmql_query="ListingPrice=200000",
                    optional_parameters={"Format": "Somecrazyformat"},
                )
                print(list(r))

    def test_auto_offset(self):
        with open("tests/rets_responses/COMPACT-DECODED/Search_1of2.xml") as f:
            search1_contents = "".join(f.readlines())

        with open("tests/rets_responses/COMPACT-DECODED/Search_2of2.xml") as f:
            search2_contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Search.ashx",
                body=search1_contents,
                status=200,
                stream=True,
            )
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Search.ashx",
                body=search2_contents,
                status=200,
                stream=True,
            )
            results_gen = self.session.search(
                resource="Property",
                resource_class="RES",
                search_filter={"ListingPrice": 200000},
            )
            results = list(results_gen)
            self.assertEqual(len(results), 6)

    def test_cache_metadata(self):
        with open("tests/rets_responses/COMPACT-DECODED/GetMetadata_table.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            self.session.get_table_metadata(resource="Property", resource_class="RES")

        self.assertIn(
            "METADATA-TABLE:Property:RES", list(self.session.metadata_responses.keys())
        )

        # Subsequent call without RequestMock should fail unless we get the saved response from metadata_responses
        table = self.session.get_table_metadata(
            resource="Property", resource_class="RES"
        )
        self.assertEqual(len(list(table)), 208)

    def test_table_metadata(self):
        with open("tests/rets_responses/COMPACT-DECODED/GetMetadata_table.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            table = self.session.get_table_metadata(
                resource="Property", resource_class="RES"
            )

        self.assertEqual(len(list(table)), 208)

    def test_lookup_type_metadata(self):
        with open("tests/rets_responses/COMPACT-DECODED/GetMetadata_lookup.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            lookup_values = self.session.get_lookup_values(
                resource="Agent", lookup_name="Broker"
            )

        self.assertEqual(len(list(lookup_values)), 61)

    def test_object_metadata(self):
        with open("tests/rets_responses/COMPACT-DECODED/GetMetadata_objects.xml") as f:
            contents = "".join(f.readlines())
        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            object_metadata = self.session.get_object_metadata(resource="Agent")

        self.assertEqual(len(list(object_metadata)), 3)

    def test_agent_digest_hash(self):
        self.session.user_agent_password = "testing"
        self.assertIsNotNone(self.session._user_agent_digest_hash())

    def test_session_cookie_name(self):
        self.assertEqual(self.session.session_id, "zacqcc1gjhkmazjznjmyrinq")

    def test_change_parser_automatically(self):
        self.assertEqual(self.session.metadata_format, "COMPACT-DECODED")

        with open("tests/rets_responses/Errors/20514.xml") as f:
            dtd_error = "".join(f.readlines())

        with open("tests/rets_responses/STANDARD-XML/GetMetadata_system.xml") as f:
            content = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=dtd_error,
                status=200,
            )
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=content,
                status=200,
            )
            self.session.get_system_metadata()

        self.assertEqual(self.session.metadata_format, "STANDARD-XML")

    def test_wildcard_lookups(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_wildcard.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            format_hold = self.session.metadata_format
            try:
                self.session.metadata_format = "STANDARD-XML"
                lookup_values = self.session.get_lookup_values(
                    resource="Property", lookup_name="*"
                )
            finally:
                self.session.metadata_format = format_hold

        self.assertEqual(len(lookup_values), 40)


class Session15Tester(unittest.TestCase):
    def setUp(self):
        super(Session15Tester, self).setUp()
        with open("tests/rets_responses/Login.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Login.ashx",
                body=contents,
                status=200,
            )
            self.session = Session(
                login_url="http://server.rets.com/rets/Login.ashx",
                username="retsuser",
                version="1.5",
            )
            self.session.metadata_format = "STANDARD-XML"
            self.session.login()

    def test_system_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_system.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            sys_metadata = self.session.get_system_metadata()

        self.assertEqual(sys_metadata["version"], "45.61.69081")
        self.assertEqual(sys_metadata["system_id"], "RETS")

    def test_resource_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_resources.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            resource = self.session.get_resource_metadata()
            self.assertEqual(len(resource), 2)

    def test_class_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_classes.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            resource_classes = self.session.get_class_metadata(resource="Agent")
            self.assertEqual(len(resource_classes), 8)

    def test_table_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_table.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            table = self.session.get_table_metadata(
                resource="Property", resource_class="1"
            )

        self.assertEqual(len(table), 162)

    def test_lookup_type_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_lookup.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            lookup_values = self.session.get_lookup_values(
                resource="Property", lookup_name="1_2"
            )

        self.assertEqual(len(lookup_values), 9)

    def test_alternative_lookup_type_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_lookup2.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            lookup_values = self.session.get_lookup_values(
                resource="Property", lookup_name="mls_cooling"
            )

        self.assertEqual(len(lookup_values), 4)

    def test_object_metadata(self):
        with open("tests/rets_responses/STANDARD-XML/GetMetadata_objects.xml") as f:
            contents = "".join(f.readlines())
        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/GetMetadata.ashx",
                body=contents,
                status=200,
            )
            object_metadata = self.session.get_object_metadata(resource="Agent")

        self.assertEqual(len(object_metadata), 1)


class LoginTester(unittest.TestCase):
    def test_login(self):
        expected_capabilities1 = {
            u"GetMetadata": u"http://server.rets.com/rets/GetMetadata.ashx",
            u"GetObject": u"http://server.rets.com/rets/GetObject.ashx",
            u"Login": u"http://server.rets.com/rets/Login.ashx",
            u"Logout": u"http://server.rets.com/rets/Logout.ashx",
            u"PostObject": u"http://server.rets.com/rets/PostObject.ashx",
            u"Search": u"http://server.rets.com/rets/Search.ashx",
            u"Update": u"http://server.rets.com/rets/Update.ashx",
        }

        expected_capabilities2 = {
            u"GetMetadata": u"http://server.rets.com/rets/GetMetadata.ashx",
            u"GetObject": u"http://server.rets.com/rets/GetObject.ashx",
            u"Login": u"http://server.rets.com/rets/Login.ashx",
            u"Logout": u"http://server.rets.com/rets/Logout.ashx",
            u"Search": u"http://server.rets.com/rets/Search.ashx",
        }

        with open("tests/rets_responses/Login.xml") as f:
            contents = "".join(f.readlines())

        with open("tests/rets_responses/Logout.html") as f:
            logout_contents = "".join(f.readlines())

        with open("tests/rets_responses/Errors/Login_no_host.xml") as f:
            no_host_contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Login.ashx",
                body=contents,
                status=200,
            )
            s = Session(
                login_url="http://server.rets.com/rets/Login.ashx",
                username="retsuser",
                version="1.5",
            )
            s.login()

            self.assertEqual(s.capabilities, expected_capabilities1)
            self.assertEquals(s.version, "1.5")

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Login.ashx",
                body=contents,
                status=200,
            )
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Logout.ashx",
                body=logout_contents,
                status=200,
            )
            with Session(
                login_url="http://server.rets.com/rets/Login.ashx",
                username="retsuser",
                version="1.7.2",
            ) as s:
                # I logged in here and will log out when leaving context
                pass

            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Login_no_host.ashx",
                body=no_host_contents,
                status=200,
                headers={"RETS-Version": "RETS/1.7.2"},
            )
            s1 = Session(
                login_url="http://server.rets.com/rets/Login_no_host.ashx",
                username="retsuser",
                version="1.5",
            )
            s1.login()

            self.assertDictEqual(s1.capabilities, expected_capabilities2)
            self.assertEquals(s.version, "1.7.2")

    def test_login_with_action(self):
        with open("tests/rets_responses/Login_with_Action.xml") as f:
            action_login = "".join(f.readlines())

        with open("tests/rets_responses/Action.xml") as f:
            action_response = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com/rets/Login_with_Action.ashx",
                body=action_login,
                status=200,
            )
            resps.add(
                resps.GET,
                "http://server.rets.com/rets/Action.ashx",
                body=action_response,
                status=200,
            )

            s2 = Session(
                login_url="http://server.rets.com/rets/Login_with_Action.ashx",
                username="retsuser",
                version="1.5",
            )
            s2.login()
            self.assertIn(u"Action", list(s2.capabilities.keys()))

    def test_port_added_to_actions(self):
        with open("tests/rets_responses/Login_relative_url.xml") as f:
            contents = "".join(f.readlines())

        with responses.RequestsMock() as resps:
            resps.add(
                resps.POST,
                "http://server.rets.com:9999/rets/Login.ashx",
                body=contents,
                status=200,
            )
            s = Session(
                login_url="http://server.rets.com:9999/rets/Login.ashx",
                username="retsuser",
                version="1.5",
            )
            s.login()

            for cap in s.capabilities.values():
                parts = urlparse(cap)
                self.assertEqual(parts.port, 9999)
