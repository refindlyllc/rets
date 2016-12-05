from rets import models
from rets.models import *
import unittest
from rets.session import Session
from datetime import datetime


class TesterWithSession(unittest.TestCase):
    # Provides a valid session object to be provided to the models during testing.
    def setUp(self):
        super(TesterWithSession, self).setUp()
        self.session = Session(login_url='http://rets.com/login.php', username='retsuser', version='1.7.2')


class LookupTester(TesterWithSession):

    def setUp(self):
        super(LookupTester, self).setUp()
        self.lookup_model = LookupTypeModel()
        self.lookup_model.ShortValue = 'The big short'

    def test_repr(self):
        self.assertEqual('<Lookup Type Metadata: The big short>', repr(self.lookup_model))


class ObjectMetadataTester(TesterWithSession):

    def setUp(self):
        super(ObjectMetadataTester, self).setUp()
        self.object_model = ObjectMetadataModel()
        self.object_model.VisibleName = 'VisiblyObjective'

    def test_repr(self):
        self.assertEqual('<Object Metadata: VisiblyObjective>', repr(self.object_model))


class ResourceTester(TesterWithSession):

    def setUp(self):
        super(ResourceTester, self).setUp()
        self.resource_model = ResourceModel()
        self.resource_model.ResourceID = 'OfficialResoureID'

    def test_repr(self):
        self.assertEqual('<Resource Metadata: OfficialResoureID>', repr(self.resource_model))

    def test_get_classes(self):
        pass

    def test_get_objects(self):
        pass


class ResourceClassTester(TesterWithSession):

    def setUp(self):
        super(ResourceClassTester, self).setUp()
        resource = ResourceModel()
        self.class_model = ResourceClassModel(resource=resource)
        self.class_model.ClassName = 'ClassName1'

    def test_repr(self):
        self.assertEqual('<Class Metadata: ClassName1>', repr(self.class_model))

    def test_get_table(self):
        pass


class TableTester(TesterWithSession):

    def setUp(self):
        super(TableTester, self).setUp()
        self.table_model = TableModel()
        self.table_model.Resource = '<Resource obj>'
        self.table_model.LookupName = 'Lookup name'
        self.table_model.SystemName = 'SystemN'

    def test_repr(self):
        self.assertEqual('<Table Metadata: SystemN>', repr(self.table_model))


class SystemTester(TesterWithSession):

    def setUp(self):
        super(SystemTester, self).setUp()
        self.system_model = SystemModel()
        self.system_model.SystemID = 'SYSTEM1'

    def test_repr(self):
        self.assertEqual('<System Metadata: SYSTEM1>', repr(self.system_model))


class RecordAndResultsTester(TesterWithSession):

    def setUp(self):
        super(RecordAndResultsTester, self).setUp()
        self.results = Results()
        self.record = Record()
        self.record.record_key = 'Nothing'  # Not actually part of a metadata results set
        self.record.set('myval', 'yourval')
        self.results.add_record(self.record)

        self.resource = ResourceModel()
        self.resource_class = ResourceClassModel(resource=self.resource).ClassName

        self.results.resource = self.resource
        self.results.resource_class = self.resource_class
        self.results.total_results_count = 10

    def test_results(self):
        self.assertEqual('<Results: 10 Found in None:None for None>', repr(self.results))
        self.assertIn(self.record, self.results.results)
        self.assertEqual(self.results.lists('myval'), ['yourval'])

        self.record.set('ListingPrice', 123000)
        self.record.record_key = 'MLSNumber'
        self.record.record_val = '222JSX'

        self.assertEqual(self.record.values['ListingPrice'], 123000)
        self.assertEqual(self.record.get('ListingPrice'), 123000)

        self.assertEqual(self.record.parent, self.results)
        self.assertEqual(self.record.resource, self.resource)
        self.assertEqual(self.record.resource_class, self.resource_class)

        self.record.set('somefield', '****')
        self.assertTrue(self.record.is_restricted('somefield'))


class ObjectTester(unittest.TestCase):

    def test_methods(self):
        o = models.object.Object()
        o.content = [1, 2, 2, 2, 2]
        self.assertEqual(5, len(o))

        o.preferred = 0
        self.assertFalse(o.is_preferred())
        o.preferred = 1
        self.assertTrue(o.is_preferred())

        o.error = True
        self.assertTrue(o.is_error())
        o.error = False
        self.assertFalse(o.is_error())
