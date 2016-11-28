from rets import models
import unittest
from rets.session import Session
from rets.configuration import Configuration
from datetime import datetime


class TesterWithSession(unittest.TestCase):
    # Provides a valid session object to be provided to the models during testing.
    def setUp(self):
        super(TesterWithSession, self).setUp()
        c = Configuration('1.7.2')
        c.login_url = 'http://rets.com/login.php'
        c.username = 'retsuser'
        self.session = Session(c)


class LookupTester(TesterWithSession):

    def setUp(self):
        super(LookupTester, self).setUp()
        self.lookup_model = models.metadata.lookup_type.LookupType(session=self.session)
        self.lookup_model.elements['ShortValue'] = 'The big short'

    def test_repr(self):
        self.assertEqual('<Lookup Type Metadata: The big short>', self.lookup_model.__repr__())


class ObjectMetadataTester(TesterWithSession):

    def setUp(self):
        super(ObjectMetadataTester, self).setUp()
        self.object_model = models.metadata.object.Object(session=self.session)
        self.object_model.elements['VisibleName'] = 'VisiblyObjective'

    def test_repr(self):
        self.assertEqual('<Object Metadata: VisiblyObjective>', self.object_model.__repr__())


class ResourceTester(TesterWithSession):

    def setUp(self):
        super(ResourceTester, self).setUp()
        self.resource_model = models.metadata.resource.Resource(session=self.session)
        self.resource_model.elements['ResourceID'] = 'OfficialResoureID'

    def test_repr(self):
        self.assertEqual('<Resource Metadata: OfficialResoureID>', self.resource_model.__repr__())

    def test_key(self):
        self.resource_model.elements['KeyField'] = 'Keytime'
        self.assertEqual(self.resource_model.key, 'Keytime')

    def test_get_classes(self):
        pass

    def test_get_objects(self):
        pass


class ResourceClassTester(TesterWithSession):

    def setUp(self):
        super(ResourceClassTester, self).setUp()
        resource = models.metadata.resource.Resource(session=self.session)
        self.class_model = models.metadata.resource_class.ResourceClass(session=self.session, resource=resource)
        self.class_model.elements['ClassName'] = 'ClassName1'

    def test_repr(self):
        self.assertEqual('<Class Metadata: ClassName1>', self.class_model.__repr__())

    def test_get_table(self):
        pass


class TableTester(TesterWithSession):

    def setUp(self):
        super(TableTester, self).setUp()
        self.table_model = models.metadata.table.Table(session=self.session)
        self.table_model.attributes['Resource'] = '<Resource obj>'
        self.table_model.elements['LookupName'] = 'Lookup name'
        self.table_model.elements['SystemName'] = 'SystemN'

    def test_repr(self):
        self.assertEqual('<Table Metadata: SystemN>', self.table_model.__repr__())

    def test_properties(self):
        self.assertEqual(self.table_model.resource, '<Resource obj>')
        self.assertEqual(self.table_model.lookup_name, 'Lookup name')

    def test_get_lookup(self):
        pass


class SystemTester(TesterWithSession):

    def setUp(self):
        super(SystemTester, self).setUp()
        self.system_model = models.metadata.system.System(session=self.session)
        self.system_model.elements['SystemID'] = 'SYSTEM1'

    def test_repr(self):
        self.assertEqual('<System Metadata: SYSTEM1>', self.system_model.__repr__())


class RecordAndResultsTester(TesterWithSession):

    def setUp(self):
        super(RecordAndResultsTester, self).setUp()
        self.results = models.search.results.Results()
        self.record = models.search.record.Record()
        self.record.set('myval', 'yourval')
        self.results.add_record(self.record)

        self.resource = models.metadata.resource.Resource(session=self.session)
        self.resource_class = models.metadata.resource_class.ResourceClass(session=self.session, resource=self.resource)

        self.results.resource = self.resource
        self.results.resource_class = self.resource_class
        self.results.total_results_count = 10

    def test_results(self):
        self.assertEqual('<Results: 10 Found>', self.results.__repr__())
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


class BulletinTester(unittest.TestCase):

    def test_properties(self):
        details = {
            'MemberName': 'First Last',
            'User': '1Agent',
            'Broker': 'BrokerUSA',
            'MetadataVersion': '1.0',
            'MetadataTimestamp': datetime(2010, 1, 1)
        }

        b = models.bulletin.Bulletin(details=details)

        b.body = 'here is the body of the response'
        self.assertEqual(b.member_name, details['MemberName'])
        self.assertEqual(b.user, details['User'])
        self.assertEqual(b.broker, details['Broker'])
        self.assertEqual(b.metadata_version, details['MetadataVersion'])
        self.assertEqual(b.metadata_timestamp, details['MetadataTimestamp'])

        b.member_name = 'New Name'
        self.assertEqual(b.member_name, 'New Name')

        b.user = 'NewUser'
        self.assertEqual(b.user, 'NewUser')

        b.broker = 'NewBroker'
        self.assertEqual(b.broker, 'NewBroker')

        b.metadata_version = '2.0'
        self.assertEqual(b.metadata_version, '2.0')

        b.metadata_timestamp = None
        self.assertIsNone(b.metadata_timestamp)


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
