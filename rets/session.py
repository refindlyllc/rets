from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
from rets.exceptions import MissingConfiguration, CapabilityUnavailable, MetadataNotFound, InvalidSearch
import logging
from rets.interpreters.get_object import GetObject
import re
import hashlib
from rets.parsers import MultipleObjectParser
from rets.parsers import SingleObjectParser
from rets.parsers import LookupTypeParser
from rets.parsers import ObjectParser
from rets.parsers import TableParser
from rets.parsers import ResourceClassParser
from rets.parsers import OneXSearchCursor
from rets.parsers import RecursiveOneXCursor
from rets.parsers import OneFiveLogin
from rets.parsers import SystemParser
from rets.parsers import ResourceParser
from rets.interpreters import SearchInterpreter
from rets.models import Bulletin
import sys

if sys.version_info < (3, 0):
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


class Session(object):

    logger = logging.getLogger(__name__)
    follow_redirecst = True
    last_request_url = None
    last_response = None
    client = requests.Session()
    capabilities = {}

    AUTH_BASIC = 'basic'
    AUTH_DIGEST = 'digest'
    allowed_auth = [AUTH_BASIC, AUTH_DIGEST]

    http_authentication = 'digest'

    def __init__(self, login_url=None, version='1.5', username=None, password=None, user_agent='Python RETS', user_agent_password=None, options={}):
        self.login_url = login_url
        self.version = version
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.user_agent_password = user_agent_password
        self.options = options

        if self.http_authentication == self.AUTH_BASIC:
            self.client.auth = HTTPBasicAuth(self.username, self.password)
        else:
            self.client.auth = HTTPDigestAuth(self.username, self.password)

        self.client.headers = {
            'User-Agent': self.user_agent,
            'RETS-Version': str(self.version),
            'Accept-Encoding': 'gzip',
            'Accept': '*/*'
        }

        if 'disable_follow_location' in self.options:
            self.follow_redirects = False

        self.add_capability(name='Login', uri=self.login_url)

    def add_capability(self, name, uri):

        parse_results = urlparse(uri)
        if parse_results.hostname is None:
            # relative URL given, so build this into an absolute URL
            login_url = self.capabilities.get('Login')
            if not login_url:
                raise ValueError("Cannot automatically determine absolute path for {} given.".format(uri))

            parts = urlparse(login_url)
            uri = parts.scheme + '://' + parts.hostname + '/' + uri

        self.capabilities[name] = uri

    def login(self):
        if None in [self.login_url, self.username]:
            raise MissingConfiguration("Cannot issue login without a valid configuration loaded")

        response = self.request('Login')
        parser = OneFiveLogin()
        parser.parse(response.text)

        for k, v in parser.capabilities.items():
            self.add_capability(k, v)

        bulletin = Bulletin(details=parser.details)
        if self.capabilities.get('Action'):
            response = self.request(self.capabilities['Action'])
            bulletin.body = response.text
            return bulletin
        else:
            return bulletin

    def get_preferred_object(self, resource, r_type, content_id, location=0):
        collection = self.get_object(resource=resource, r_type=r_type,
                                     content_ids=content_id, object_ids='0', location=location)
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
            parser = MultipleObjectParser()
            collection = parser.parse(response)
        else:
            parser = SingleObjectParser()
            parser.parse(response)
            collection = [parser.parse(response)]

        return collection

    def get_system_metadata(self):
        parser = SystemParser(version=self.version)
        return self.make_metadata_request(meta_type='METADATA-SYSTEM', meta_id=0, parser=parser)

    def get_resources_metadata(self, resource_id=None):
        parser = ResourceParser()
        result = self.make_metadata_request(meta_type='METADATA-RESOURCE', meta_id=0, parser=parser)

        if resource_id:
            for name, r in result.items():
                if name == resource_id:
                    return r
            raise MetadataNotFound("Requested {} resource metadata does not exist".format(resource_id))

        return result

    def get_classes_metadata(self, resource_id):
        parser = ResourceClassParser()
        return self.make_metadata_request(meta_type='METADATA-CLASS', meta_id=resource_id, parser=parser)

    def get_table_metadata(self, resource_id, class_id):
        parser = TableParser()
        return self.make_metadata_request(meta_type='METADATA-TABLE', meta_id=resource_id + ':' + class_id, parser=parser)

    def get_object_metadata(self, resource_id):
        parser = ObjectParser()
        return self.make_metadata_request(meta_type='METADATA-OBJECT', meta_id=resource_id, parser=parser)

    def get_lookup_values(self, resource_id, lookup_name):
        parser = LookupTypeParser()
        return self.make_metadata_request(meta_type='METADATA-LOOKUP_TYPE', meta_id=resource_id + ':' + lookup_name, parser=parser)

    def make_metadata_request(self, meta_type, meta_id, parser):
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
        return parser.parse(response)

    def search(self, resource_id, class_id, search_filter=None, dmql_query=None, optional_parameters=None, recursive=False):
        if not optional_parameters:
            optional_parameters = {}

        if (search_filter and dmql_query) or (not search_filter and not dmql_query):
            raise InvalidSearch("You may specify either a search_filter or dmql_query")

        search_interpreter = SearchInterpreter()

        if dmql_query:
            dmql_query = search_interpreter.dmql(query=dmql_query)
        else:
            dmql_query = search_interpreter.filter_to_dmql(filter_dict=search_filter)

        parameters = {
            'SearchType': resource_id,
            'Class': class_id,
            'Query': dmql_query,
            'QueryType': 'DMQL2',
            'Count': 1,
            'Format': 'COMPACT-DECODED',
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
            parser = RecursiveOneXCursor()
        else:
            parser = OneXSearchCursor()

        return parser.parse(rets_response=response, parameters=parameters)

    def disconnect(self):
        self.request(capability='Logout')
        return True

    def request(self, capability, options=None):
        if options is None:
            options = {}

        options.update({
            'headers': self.client.headers.copy()
        })

        url = self.capabilities.get(capability)

        if not url:
            raise CapabilityUnavailable("{} tried but no valid endpoints was found. Did you forget to Login()".format(capability))

        if self.user_agent_password:
            ua_digest = self.user_agent_digest_hash()
            options['headers']['RETS-UA-Authorization'] = 'Digest {}'.format(ua_digest)

        print("Sending HTTP Request for {}".format(capability))

        if 'query' in options:
            query_str = '?' + '&'.join('{}={}'.format(k, v) for k, v in options['query'].items())
            self.last_request_url = url + query_str
        else:
            query_str = ''
            self.last_request_url = url

        if self.options.get('use_post_method'):
            print('Using POST method per use_post_method option')
            query = options.get('query')
            response = self.client.post(url, data=query, headers=options['headers'])
        else:
            response = self.client.get(url + query_str, headers=options['headers'])

        print("Response: HTTP {}".format(response.status_code))
        return response

    def user_agent_digest_hash(self):
        ua_a1 = hashlib.md5('{0}:{1}'
                            .format(self.user_agent.strip(), self.user_agent_password.strip())
                            .encode('utf-8')).digest()
        return ua_a1
