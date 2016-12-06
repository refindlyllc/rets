from rets.session import Session
import unittest
import os
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


class SessionTester(unittest.TestCase):
    @unittest.skip
    def test_session(self):
        login_url = os.environ.get("RETS_LOGIN_URL")
        username = os.environ.get("RETS_USERNAME")
        password = os.environ.get("RETS_PASSWORD")
        with Session(login_url=login_url, username=username, password=password, version='1.7') as s:
            self.assertIsNotNone(s)
            system = s.get_system_metadata()
            self.assertIsNotNone(system)
            #search_res = s.search(resource='Property', class_id='RES', dmql_query='(Status=S)')
            #self.assertIsNotNone(search_res)
            fields = s.get_table_metadata(resource='Property', resource_class='RES')
            self.assertIsNotNone(fields)
            objects = s.get_object_metadata(resource='Property')
            self.assertIsNotNone(objects)

        resources = s.get_resource_metadata()
        '''
        self.assertIsNotNone(resources)

        r_classes = {}
        for r, v in resources.items():
            r_classes[r] = s.get_classes_metadata(r)
        self.assertIsNotNone(r_classes)
        objects = s.get_object(resource='Property', r_type='Photo', content_ids='2228878', object_ids='*', location=0)
        self.assertIsNotNone(objects)

        fields = s.get_table_metadata(resource_id='Property', class_id='RES')
        self.assertIsNotNone(fields)
        #objects = s.get_object_metadata(resource_id='Property')
        #self.assertIsNotNone(objects)

        search_res = s.search(resource_id='Property', class_id='RES', dmql_query='(ListPrice=150000+)', optional_parameters={'Limit': 3})
        self.assertIsNotNone(search_res)
        '''


