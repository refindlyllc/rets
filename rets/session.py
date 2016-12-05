from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
from rets.exceptions import MissingConfiguration, CapabilityUnavailable, MetadataNotFound, InvalidSearch, \
    UnexpectedParserType, RETSException
import logging
from rets.utils.get_object import GetObject
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
from rets.utils import DMQLHelper
import sys

if sys.version_info < (3, 0):
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

logger = logging.getLogger('rets')
AUTH_BASIC = 'basic'
AUTH_DIGEST = 'digest'
SUPPORTED_VERSIONS = ['1.5', '1.7', '1.7.2', '1.8']


class Session(object):

    logger = logging.getLogger(__name__)
    last_request_url = None
    last_response = None
    client = requests.Session()
    capabilities = {}

    AUTH_BASIC = 'basic'
    AUTH_DIGEST = 'digest'
    allowed_auth = [AUTH_BASIC, AUTH_DIGEST]

    def __init__(self, login_url, username, password=None, version='1.5', http_auth='digest',
                 user_agent='Python RETS', user_agent_password=None, options={}, cache_metadata=True,
                 follow_redirects=True, use_post_method=False):
        """
        Session constructor
        :param login_url: The login URL for the RETS feed
        :param version: The RETS version to use. Default is 1.5
        :param username: The username for the RETS feed
        :param password: The password for the RETS feed
        :param user_agent: The useragent for the RETS feed
        :param user_agent_password: The useragent password for the RETS feed
        :param follow_redirects: Follow HTTP redirects or not. The default is to follow them, True.
        :param use_post_method: Use HTTP POST method when making requests instead of GET. The default is False
        """
        self.login_url = login_url
        self.version = version
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.user_agent_password = user_agent_password
        self.options = options
        self.http_authentication = http_auth
        self.cache_metadata = cache_metadata

        if version not in SUPPORTED_VERSIONS:
            logger.error("Attempted to initialize a session with an invalid RETS version.")
            raise MissingConfiguration("The version parameter of {} is not currently supported.".format(version))
        self.version = version

        self.metadata_responses = {}  # Keep metadata in the session instance to avoid consecutive calls to RETS

        self.last_request_url = None
        self.last_response = None
        self.capabilities = {}
        self.allowed_auth = [AUTH_BASIC, AUTH_DIGEST]

        self.client = requests.Session()
        if self.http_authentication == AUTH_BASIC:
            self.client.auth = HTTPBasicAuth(self.username, self.password)
        else:
            self.client.auth = HTTPDigestAuth(self.username, self.password)

        self.client.headers = {
            'User-Agent': self.user_agent,
            'RETS-Version': str(self.version),
            'Accept-Encoding': 'gzip',
            'Accept': '*/*'
        }

        self.follow_redirects = follow_redirects
        self.use_post_method = use_post_method

        self.add_capability(name='Login', uri=self.login_url)
        self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Logging out")
        self.disconnect()

    def add_capability(self, name, uri):
        """
        Add a capability of the RETS board
        :param name: The name of the capability
        :param uri: The capability URI given by the RETS board
        :return: None
        """

        parse_results = urlparse(uri)
        if parse_results.hostname is None:
            # relative URL given, so build this into an absolute URL
            login_url = self.capabilities.get('Login')
            if not login_url:
                logger.error("There is no login URL stored, so additional capabilities cannot be added.")
                raise ValueError("Cannot automatically determine absolute path for {} given.".format(uri))

            parts = urlparse(login_url)
            uri = parts.scheme + '://' + parts.hostname + '/' + uri

        self.capabilities[name] = uri

    def login(self):
        """
        Login to the RETS board and return an instance of Bulletin
        :return: Bulletin instance
        """
        if None in [self.login_url, self.username]:
            logger.error("The RETS session cannot login without a login_url and a username at a minimum.")
            raise MissingConfiguration("Cannot issue login without a valid configuration loaded")

        response = self.request('Login')
        if response.status_code == 401:
            raise RETSException("Invalid login credentials. 401 Status code received from the RETS server.")
        parser = OneFiveLogin()
        parser.parse(response.text)

        for k, v in parser.capabilities.items():
            self.add_capability(k, v)

        if self.capabilities.get('Action'):
            self.request(self.capabilities['Action'])
        return True

    def get_preferred_object(self, resource, r_type, content_id, location=0):
        """
        Get the first object from a Resource
        :param resource: The name of the resource
        :param r_type: The type of object to fetch
        :param content_id: The unique id of the item to get objects for
        :param location: The path to get Objects from
        :return: Object
        """
        collection = self.get_object(resource=resource, r_type=r_type,
                                     content_ids=content_id, object_ids='0', location=location)
        return collection[0]

    def get_object(self, resource, r_type, content_ids, object_ids='*', location=0):
        """
        Get a list of Objects from a resource
        :param resource: The resource to get objects from
        :param r_type: The type of object to fetch
        :param content_ids: The unique id of the item to get objects for
        :param object_ids: ids of the objects to download
        :param location: The path to get Objects from
        :return: list
        """
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
        """
        Get the top level metadata
        :return: SystemModel
        """
        parser = SystemParser(version=self.version)
        return self.make_metadata_request(meta_id=0, parser=parser)

    def get_resource_metadata(self, resource_id=None):
        """
        Get resource metadata
        :param resource_id: The name of the resource to get metadata for
        :return: ResourceModel
        """
        parser = ResourceParser()
        result = self.make_metadata_request(meta_id=0, parser=parser)

        if resource_id:
            for name, r in result.items():
                if name == resource_id:
                    return r
            raise MetadataNotFound("Requested resource metadata does not exist")

        return result

    def get_classes_metadata(self, resource_id):
        """
        Get classes for a given resource
        :param resource_id: The resource name to get class metadata for
        :return: ResourceClassModel
        """
        parser = ResourceClassParser()
        return self.make_metadata_request(meta_id=resource_id, parser=parser)

    def get_table_metadata(self, resource_id, class_id):
        """
        Get metadata for a given resource: class
        :param resource_id: The name of the resource
        :param class_id: The name of the class to get metadata from
        :return: TableModel
        """
        parser = TableParser()
        return self.make_metadata_request(meta_id=resource_id + ':' + class_id, parser=parser)

    def get_object_metadata(self, resource_id):
        """
        Get object metadata from a resource
        :param resource_id: The resource name to get object metadata for
        :return: ObjectMetadataModel
        """
        parser = ObjectParser()
        return self.make_metadata_request(meta_id=resource_id, parser=parser)

    def get_lookup_values(self, resource_id, lookup_name):
        """
        Get possible lookup values for a given field
        :param resource_id: The name of the resource
        :param lookup_name: The name of the the field to get lookup values for
        :return: LookUpTypeModel
        """
        parser = LookupTypeParser()
        return self.make_metadata_request(meta_id=resource_id + ':' + lookup_name, parser=parser)

    def make_metadata_request(self, meta_id, parser):
        """
        Get the Metadata
        :param meta_id: The name of the resource, class, or lookup to get metadata for
        :param parser: An instance of the parser to parser the response
        :return: dict
        """
        class_type_to_meta_type = {
            ResourceClassParser: 'METADATA-CLASS',
            TableParser: 'METADATA-TABLE',
            ObjectParser: 'METADATA-OBJECT',
            LookupTypeParser: 'METADATA-LOOKUP_TYPE',
            SystemParser: 'METADATA-SYSTEM',
            ResourceParser: 'METADATA-RESOURCE'
        }

        if class_type_to_meta_type.get(type(parser)) is None:
            raise UnexpectedParserType("Unexpected parser type given: " + str(type(parser)))

        meta_type = class_type_to_meta_type.get(type(parser))

        # If this metadata request has already happened, returned the saved result.
        key = '{}:{}'.format(meta_type, meta_id)
        if key in self.metadata_responses and self.cache_metadata:
            response = self.metadata_responses[key]
        else:
            response = self.request(
                capability='GetMetadata',
                options={
                    'query': {
                        'Type': meta_type,
                        'ID': meta_id,
                        'Format': 'COMPACT'
                    }
                }
            )
            self.metadata_responses[key] = response
        return parser.parse(response)

    def search(self, resource_id, class_id, search_filter=None, dmql_query=None, optional_parameters=None, recursive=False):
        """
        Preform a search on the RETS board
        :param resource_id: The resource that contains the class to search
        :param class_id: The class to search in
        :param search_filter: The query as a dict
        :param dmql_query: The query in dmql format
        :param optional_parameters: Values for option paramters
        :param recursive: if True, automatically account for offsets to get all data
        :return: dict
        """
        if not optional_parameters:
            optional_parameters = {}

        if (search_filter and dmql_query) or (not search_filter and not dmql_query):
            raise InvalidSearch("You may specify either a search_filter or dmql_query")

        search_interpreter = DMQLHelper()

        if dmql_query:
            dmql_query = search_interpreter.dmql(query=dmql_query)
        else:
            dmql_query = search_interpreter.filter_to_dmql(filter_dict=search_filter)

        parameters = {
            'SearchType': resource_id,
            'Class': class_id,
            'ResourceMetadata': self.get_resource_metadata(resource_id=resource_id),
            'Query': dmql_query,
            'QueryType': 'DMQL2',
            'Count': 1,
            'Format': 'COMPACT',
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
        """
        Logs out of the RETS feed destroying the HTTP session.
        :return: True
        """
        self.request(capability='Logout')
        return True

    def request(self, capability, options=None):
        """
        Make a request to the RETS server
        :param capability: The name of the capability to use to get the URI
        :param options: Options to put into the request
        :return: Response
        """
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

        logger.debug("Sending HTTP Request for {}".format(capability))

        if 'query' in options:
            query_str = '?' + '&'.join('{}={}'.format(k, v) for k, v in options['query'].items())
            self.last_request_url = url + query_str
        else:
            query_str = ''
            self.last_request_url = url

        if self.use_post_method:
            logger.debug('Using POST method per use_post_method option')
            query = options.get('query')
            response = self.client.post(url, data=query, headers=options['headers'])
        else:
            url += query_str
            response = self.client.get(url, headers=options['headers'])

        logger.debug("Response: HTTP {}".format(response.status_code))
        return response

    def user_agent_digest_hash(self):
        """
        Hash the user agent and user agent password
        :return: md5
        """
        ua_a1 = hashlib.md5('{0}:{1}'
                            .format(self.user_agent.strip(), self.user_agent_password.strip())
                            .encode('utf-8')).digest()
        return ua_a1
