from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
import hashlib
import logging
import sys
from rets.exceptions import InvalidSearch, RETSException, NotLoggedIn, AutomaticPaginationError, EmptySearchResults
from rets.utils.get_object import GetObject
from rets.parsers.get_object import MultipleObjectParser
from rets.parsers.get_object import SingleObjectParser
from rets.parsers.search import OneXSearchCursor
from rets.parsers.login import OneXLogin
from rets.parsers.metadata import Metadata
from rets.utils import DMQLHelper

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

logger = logging.getLogger('rets')


class Session(object):

    allowed_auth = ['basic', 'digest']
    supported_versions = ['1.5', '1.7', '1.7.2', '1.8']

    def __init__(self, login_url, username, password=None, version='1.5', http_auth='digest',
                 user_agent='Python RETS', user_agent_password=None, cache_metadata=True,
                 follow_redirects=True, use_post_method=True):
        """
        Session constructor
        :param login_url: The login URL for the RETS feed
        :param version: The RETS version to use. Default is 1.5
        :param username: The username for the RETS feed
        :param password: The password for the RETS feed
        :param user_agent: The useragent for the RETS feed
        :param user_agent_password: The useragent password for the RETS feed
        :param follow_redirects: Follow HTTP redirects or not. The default is to follow them, True.
        :param use_post_method: Use HTTP POST method when making requests instead of GET. The default is True
        """
        self.client = requests.Session()
        self.login_url = login_url
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.user_agent_password = user_agent_password
        self.http_authentication = http_auth
        self.cache_metadata = cache_metadata
        self.capabilities = {}

        if version not in self.supported_versions:
            logger.error("Attempted to initialize a session with an invalid RETS version.")
            raise RETSException("The version parameter of {0!s} is not currently supported.".format(version))
        self.version = version

        self.metadata_responses = {}  # Keep metadata in the session instance to avoid consecutive calls to RETS

        self.capabilities = {}

        self.client = requests.Session()
        if self.http_authentication == 'basic':
            self.client.auth = HTTPBasicAuth(self.username, self.password)
        else:
            self.client.auth = HTTPDigestAuth(self.username, self.password)

        self.client.headers = {
            #'User-Agent': self.user_agent,
            #'RETS-Version': str(self.version),
            # 'Accept-Encoding': 'gzip',
            #'Accept': '*/*'
        }

        self.follow_redirects = follow_redirects
        self.use_post_method = use_post_method
        self.add_capability(name=u'Login', uri=self.login_url)

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

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
                raise ValueError("Cannot automatically determine absolute path for {0!s} given.".format(uri))

            parts = urlparse(login_url)
            uri = parts.scheme + '://' + parts.hostname + '/' + uri.lstrip('/')

        self.capabilities[name] = uri

    def login(self):
        """
        Login to the RETS board and return an instance of Bulletin
        :return: Bulletin instance
        """
        response = self._request('Login')
        parser = OneXLogin()
        parser.parse(response.text)
        parser.parse_headers(response.headers)
        if parser.headers.get('RETS-Version', None) is not None and parser.headers.get('RETS-Version') != self.version:
            logger.debug("The server returned a different RETS version than supplied. This will be automatically"
                         " corrected for you.")
            self.version = str(parser.headers.get('RETS-Version')).strip('RETS/')
            self.client.headers['RETS-Version'] = self.version

        for k, v in parser.capabilities.items():
            self.add_capability(k, v)

        if self.capabilities.get('Action'):
            self._request(self.capabilities['Action'])
        return True

    def logout(self):
        """
        Logs out of the RETS feed destroying the HTTP session.
        :return: True
        """
        logger.debug("Logging out of RETS session.")
        self._request(capability='Logout')
        return True

    def get_system_metadata(self):
        """
        Get the top level metadata
        :return: list
        """
        result = self._make_metadata_request(meta_id=0, metadata_type='METADATA-SYSTEM')
        # Get dict out of list
        return result.pop()

    def get_resource_metadata(self, resource=None):
        """
        Get resource metadata
        :param resource_id: The name of the resource to get metadata for
        :return: list
        """
        result = self._make_metadata_request(meta_id=0, metadata_type='METADATA-RESOURCE')
        if resource:
            result = next((item for item in result if item['ResourceID'] == resource), None)
            if not result:
                raise RETSException("Could not find resource information for the given resource.")
        return result

    def get_class_metadata(self, resource):
        """
        Get classes for a given resource
        :param resource: The resource name to get class metadata for
        :return: list
        """
        return self._make_metadata_request(meta_id=resource, metadata_type='METADATA-CLASS')

    def get_table_metadata(self, resource, resource_class):
        """
        Get metadata for a given resource: class
        :param resource: The name of the resource
        :param resource_class: The name of the class to get metadata from
        :return: list
        """
        return self._make_metadata_request(meta_id=resource + ':' + resource_class, metadata_type='METADATA-TABLE')

    def get_object_metadata(self, resource):
        """
        Get object metadata from a resource
        :param resource: The resource name to get object metadata for
        :return: list
        """
        return self._make_metadata_request(meta_id=resource, metadata_type='METADATA-OBJECT')

    def get_lookup_values(self, resource, lookup_name):
        """
        Get possible lookup values for a given field
        :param resource: The name of the resource
        :param lookup_name: The name of the the field to get lookup values for
        :return: list
        """
        return self._make_metadata_request(meta_id=resource + ':' + lookup_name, metadata_type='METADATA-LOOKUP_TYPE')

    def _make_metadata_request(self, meta_id, metadata_type=None):
        """
        Get the Metadata
        :param meta_id: The name of the resource, class, or lookup to get metadata for
        :param metadata_type: The RETS metadata type
        :return: list
        """
        parser = Metadata()
        # If this metadata _request has already happened, returned the saved result.
        key = '{0!s}:{1!s}'.format(metadata_type, meta_id)
        if key in self.metadata_responses and self.cache_metadata:
            response = self.metadata_responses[key]
        else:
            response = self._request(
                capability='GetMetadata',
                options={
                    'query': {
                        'Type': metadata_type,
                        'ID': meta_id,
                        'Format': 'COMPACT-DECODED'
                    }
                }
            )
            self.metadata_responses[key] = response
        return parser.parse(response=response, metadata_type=metadata_type, rets_version=self.version)

    def get_preferred_object(self, resource, object_type, content_id, location=0):
        """
        Get the first object from a Resource
        :param resource: The name of the resource
        :param object_type: The type of object to fetch
        :param content_id: The unique id of the item to get objects for
        :param location: The path to get Objects from
        :return: Object
        """
        collection = self.get_object(resource=resource, object_type=object_type,
                                     content_ids=content_id, object_ids='0', location=location)
        return collection[0]

    def get_object(self, resource, object_type, content_ids, object_ids='*', location=0):
        """
        Get a list of Objects from a resource
        :param resource: The resource to get objects from
        :param object_type: The type of object to fetch
        :param content_ids: The unique id of the item to get objects for
        :param object_ids: ids of the objects to download
        :param location: The path to get Objects from
        :return: list
        """
        object_helper = GetObject()
        request_ids = object_helper.ids(content_ids=content_ids, object_ids=object_ids)

        response = self._request(
            capability='GetObject',
            options={
                'query':
                    {
                        "Resource": resource,
                        "Type": object_type,
                        "ID": ','.join(request_ids),
                        "Location": location
                    }
            }
        )

        if 'multipart' in response.headers.get('Content-Type'):
            parser = MultipleObjectParser()
            collection = parser.parse(response)
        else:
            parser = SingleObjectParser()
            parser.parse(response)
            collection = [parser.parse(response)]

        return collection

    def search(self, resource, resource_class, search_filter=None, dmql_query=None, limit=None, offset=None,
               optional_parameters=None):
        """
        Preform a search on the RETS board
        :param resource: The resource that contains the class to search
        :param resource_class: The class to search
        :param search_filter: The query as a dict
        :param dmql_query: The query in dmql format
        :param limit: Limit search values count
        :param offset: Offset for RETS request. Useful when RETS limits number of results or transactions
        :param optional_parameters: Values for option paramters
        :param recursive: Should the search be allowed to trigger subsequent searches.
        :return: dict
        """

        if (search_filter and dmql_query) or (not search_filter and not dmql_query):
            raise InvalidSearch("You may specify either a search_filter or dmql_query")

        search_helper = DMQLHelper()

        if dmql_query:
            dmql_query = search_helper.dmql(query=dmql_query)
        else:
            dmql_query = search_helper.filter_to_dmql(filter_dict=search_filter)

        parameters = {
            'SearchType': resource,
            'Class': resource_class,
            'Query': dmql_query,
            'QueryType': 'DMQL2',
            'Count': 1,
            'Format': 'COMPACT-DECODED',
            'StandardNames': 0,
        }

        if not optional_parameters:
            optional_parameters = {}
        parameters.update(optional_parameters)

        # if the Select parameter given is an array, format it as it needs to be
        if 'Select' in parameters and type(parameters.get('Select')) is list:
            parameters['Select'] = ','.join(parameters['Select'])

        if limit:
            parameters['Limit'] = limit

        if offset:
            parameters['Offset'] = offset

        search_cursor = OneXSearchCursor()
        response = self._request(
            capability='Search',
            options={
                'query': parameters,
            },
            stream=True
        )
        return search_cursor.generator(response=response)

    def _request(self, capability, options=None, stream=False):
        """
        Make a _request to the RETS server
        :param capability: The name of the capability to use to get the URI
        :param options: Options to put into the _request
        :return: Response
        """
        if options is None:
            options = {}

        options.update({
            'headers': self.client.headers.copy()
        })

        url = self.capabilities.get(capability)

        if not url:
            msg = "{0!s} tried but no valid endpoints was found. Did you forget to Login()".format(capability)
            raise RETSException(msg)

        if self.user_agent_password:
            ua_digest = self._user_agent_digest_hash()
            options['headers']['RETS-UA-Authorization'] = 'Digest {0!s}'.format(ua_digest)

        logger.debug("Sending HTTP Request for {0!s}".format(capability))

        if self.use_post_method:
            logger.debug('Using POST method per use_post_method option')
            query = options.get('query')
            response = self.client.post(url, data=query, headers=options['headers'], stream=stream)
        else:
            if 'query' in options:
                url += '?' + '&'.join('{0!s}={1!s}'.format(k, v) for k, v in options['query'].items())

            response = self.client.get(url, headers=options['headers'], stream=stream)
            #from urllib.request import urlopen
            #response = urlopen(url)

        '''
        logger.debug("Response: HTTP {0!s}".format(response.status_code))
        if response.status_code == 401:
            raise NotLoggedIn("The RETS server returned a 401 status code. You must be logged in to make this _request.")

        if response.status_code == 404 and self.use_post_method:
            raise RETSException("Got a 404 when making a POST _request. Try setting use_post_method=False when "
                                "initializing the Session.")
        '''
        return response

    def _user_agent_digest_hash(self):
        """
        Hash the user agent and user agent password
        :return: md5
        """
        ua_a1 = hashlib.md5('{0!s}:{1!s}'
                            .format(self.user_agent.strip(), self.user_agent_password.strip())
                            .encode('utf-8')).digest()
        return ua_a1
