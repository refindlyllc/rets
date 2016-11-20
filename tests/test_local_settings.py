from rets.configuration import Configuration
from rets.session import Session
import unittest
import os
from mock import patch


class SessionTester(unittest.TestCase):

    def test_session(self):
        c = Configuration('1.7.2')
        c.login_url = os.environ.get("RETS_LOGIN_URL")
        c.username = os.environ.get("RETS_USERNAME")
        c.password = os.environ.get("RETS_PASSWORD")

        s = Session(c)
        self.assertIsNotNone(s)

        s.login()

        system = s.get_system_metadata()

        self.assertIsNotNone(system)
        resources = s.get_resources_metadata()

        self.assertIsNotNone(resources)

        r_classes = {}
        for r, v in resources.items():
            r_classes[r] = s.get_classes_metadata(r)
        self.assertIsNotNone(r_classes)
        objects = s.get_object(resource='Property', r_type='Photo', content_ids='2228878', object_ids='*', location=0)
        self.assertIsNotNone(objects)
        fields = s.get_table_metadata(resource_id='Property', class_id='RES')
        self.assertIsNotNone(fields)
        search_res = s.search(resource_id='Property', class_id='RES', dqml_query='(ListPrice=150000+)', optional_parameters={'Limit': 3})
        self.assertIsNotNone(search_res)
