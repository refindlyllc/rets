from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
from .exceptions import MissingConfiguration, CapabilityUnavailable, MetadataNotFound
import logging
from rets.capabilities import Capabilities
from rets.interpreters.get_object import GetObject
import re
from .parsers.get_object.multiple import Multiple
from .parsers.get_object.single import Single
from .parsers.get_metadata.lookup_type import LookupType
from .parsers.get_metadata.object import Object
from .parsers.get_metadata.table import Table
from .parsers.get_metadata.resource_class import ResourceClass
from .parsers.search.one_x import OneX
from .parsers.search.recursive_one_x import RecursiveOneX
from .interpreters.search import Search
from .parsers.login.one_five import OneFive
from .parsers.get_metadata.system import System
from .parsers.get_metadata.resource import Resource
from .models.bulletin import Bulletin


class Session(object):

    logger = logging.getLogger(__name__)
    rets_session_id = None
    follow_redirecst = True
    capabilities = Capabilities()
    last_request_url = None
    last_response = None
    cookie = None

    def __init__(self, configuration):
        self.configuration = configuration

        self.client = requests.Session()
        if self.configuration.http_authentication == self.configuration.AUTH_BASIC:
            self.client.auth = HTTPBasicAuth(self.configuration.username, self.configuration.password)
        else:
            self.client.auth = HTTPDigestAuth(self.configuration.username, self.configuration.password)

        self.client.headers = {
            'User-Agent': self.configuration.user_agent,
            'RETS-Version': str(self.configuration.rets_version),
            'Accept-Encoding': 'gzip',
            'Accept': '*/*'
        }

        if 'disable_follow_location' in self.configuration.options:
            self.follow_redirects = False

        self.capabilities.add(name='Login', uri=self.configuration.login_url)

    def login(self):
        if not self.configuration.is_valid():
            raise MissingConfiguration("Cannot issue login without a valid configuration loaded")

        response = self.request('Login')
        parser = OneFive()
        parser.parse(response.text)

        for k, v in parser.capabilities.items():
            self.capabilities.add(k, v)

        bulletin = Bulletin(details=parser.details)
        if self.capabilities.capabilities.get('Action'):
            response = self.request(self.capabilities.capabilities['Action'])
            bulletin.body = response.text
            return bulletin
        else:
            return bulletin

    def get_preferred_object(self, resource, r_type, content_id, location=0):
        collection = self.get_object(resource, r_type,content_id, 0, location)
        return collection[0]

    def get_object(self, resource, r_type, content_ids, object_ids='*', location=0):
        request_ids = GetObject().ids(content_ids=content_ids, object_ids=object_ids)

        response = self.request(
            capability='GetObject',
            options={
                'query':
                    {
                        "Resource": resource,
                        "Type": r_type,
                        "ID": ','.join(request_ids),
                        "Location": location
                    }
            }
        )

        if re.match(pattern='/multipart/', string=response.headers.get('Content-Type')):
            parser = Multiple()
            collection = parser.parse(response)
        else:
            parser = Single()
            parser.parse(response)
            collection = [response]

        return collection

    def get_system_metadata(self):
        parser = System()
        return self.make_metadata_request('METADATA-SYSTEM', 0, parser=parser)

    def get_resources_metadata(self, resource_id=None):
        parser = Resource()
        result = self.make_metadata_request('METADATA-RESOURCE', 0, parser=parser)

        if resource_id:
            for r in result:
                if r.resource_id == resource_id:
                    return r
            raise MetadataNotFound("Requested {} resource metadata does not exist".format(resource_id))

        return result

    def get_classes_metadata(self, resource_id):
        parser = ResourceClass()
        return self.make_metadata_request('METADATA-CLASS', resource_id, parser)

    def get_table_metadata(self, resource_id, class_id, keyed_by='SystemName'):
        parser = Table()
        return self.make_metadata_request('METADATA-TABLE', resource_id + ':' + class_id, parser, keyed_by)

    def get_object_metadata(self, resource_id):
        parser = Object()
        return self.make_metadata_request('METADATA-OBJECT', resource_id, parser)

    def get_lookup_values(self, resource_id, lookup_name):
        parser = LookupType()
        return self.make_metadata_request('METADATA-LOOKUP_TYPE', resource_id + ':' + lookup_name, parser)

    def make_metadata_request(self, meta_type, meta_id, parser, keyed_by=None):
        response = self.request(
            capability='GetMetadata',
            options={
                'query': {
                    'Type': meta_type,
                    'ID': meta_id,
                    'Format': 'STANDARD-XML'
                }
            }
        )
        return parser.parse(self, response, keyed_by)

    def search(self, resource_id, class_id, dqml_query, optional_parameters=None, recursive=False):
        if not optional_parameters:
            optional_parameters = {}

        dqml_query = Search().dmqp(dqml_query)

        parameters = {
            'SearchType': resource_id,
            'Class': class_id,
            'Query': dqml_query,
            'QueryType': 'DQML2',
            'Count': 1,
            'Format': 'COMPACT_DECODED',
            'Limit': 99999999,
            'StandardNames': 0
        }

        parameters.update(optional_parameters)

        # if the Select parameter given is an array, format it as it needs to be
        if 'Select' in parameters:
            if type(parameters['Select']) is list:
                parameters['Select'] = ','.join(parameters['Select'])

        response = self.request(
            capability='Search',
            options={
                'query': parameters
            }
        )

        if recursive:
            parser = RecursiveOneX()
        else:
            parser = OneX()

        return parser.parse(rets_session=self, response=response, parameters=parameters)


    def disconnect(self):
        self.request(capability='Logout')
        return True

    def request(self, capability, options=None):
        if options is None:
            options = {}

        options.update({
            'headers': self.client.headers.copy()
        })

        url = self.capabilities.capabilities.get(capability)

        if not url:
            raise CapabilityUnavailable("{} tried but no valid endpoints was found. Did you forget to Login()".format(capability))

        if self.configuration.user_agent_password:
            ua_digest = self.configuration.user_agent_digest_hash(self)
            options['headers']['RETS-UA-Authorization'] = 'Digest {}'.format(ua_digest)

        print("Sending HTTP Request for {}".format(capability))

        if 'query' in options:
            query_str = '?' + '&'.join('{}={}'.format(k, v) for k, v in options['query'].items())
            self.last_request_url = url + query_str
        else:
            query_str = ''
            self.last_request_url = url

        if self.configuration.options.get('use_post_method'):
            print('Using POST method per use_post_method option')
            query = options.get('query')
            response = self.client.post(url, data=query, headers=options['headers'])
        else:
            response = self.client.get(url + query_str, headers=options['headers'])

        print("Response: HTTP {}".format(response.status_code))
        return response
