import hashlib
import logging

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from six.moves.urllib.parse import urlparse, quote


from rets.exceptions import NotLoggedIn, MissingVersion, HTTPException, RETSException, MaxrowException
from rets.parsers.get_object import MultipleObjectParser
from rets.parsers.get_object import SingleObjectParser
from rets.parsers.login import OneXLogin
from rets.parsers.metadata import CompactMetadata, StandardXMLetadata
from rets.parsers.search import OneXSearchCursor
from rets.utils import DMQLHelper
from rets.utils.get_object import GetObject


logger = logging.getLogger('rets')


class Session(object):
    """The Session object that makes requests to the RETS Server"""

    allowed_auth = ['basic', 'digest']

    def __init__(self, login_url, username, password=None, version=None, http_auth='digest',
                 user_agent='Python RETS', user_agent_password=None, cache_metadata=True,
                 follow_redirects=True, use_post_method=True, metadata_format='COMPACT-DECODED'):
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
        :param metadata_format: COMPACT_DECODED or STANDARD_XML. The client will attempt to set this automatically
        based on response codes from the RETS server.
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
        self.version = version  # Set by the RETS server response at login. You can override on initialization.

        self.metadata_responses = {}  # Keep metadata in the session instance to avoid consecutive calls to RETS
        self.metadata_format = metadata_format
        self.capabilities = {}

        self.client = requests.Session()
        self.session_id = None
        if self.http_authentication == 'basic':
            self.client.auth = HTTPBasicAuth(self.username, self.password)
        else:
            self.client.auth = HTTPDigestAuth(self.username, self.password)

        self.client.headers = {
            'User-Agent': self.user_agent,
            'Accept-Encoding': 'gzip',
            'Accept': '*/*'
        }

        if self.version:
            self.client.headers['RETS-Version'] = '{0!s}'.format(self.version)

        self.follow_redirects = follow_redirects
        self.use_post_method = use_post_method
        self.add_capability(name=u'Login', uri=self.login_url)

    def __enter__(self):
        """Context Manager: Login when entering context"""
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager: Logout when leaving context"""
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
        parser.parse(response)

        self.session_id = response.cookies.get('RETS-Session-ID', '')

        if parser.headers.get('RETS-Version') is not None:
            self.version = str(parser.headers.get('RETS-Version'))
            self.client.headers['RETS-Version'] = self.version

        for k, v in parser.capabilities.items():
            self.add_capability(k, v)

        if self.capabilities.get('Action'):
            self._request('Action')
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
        :param resource: The name of the resource to get metadata for
        :return: list
        """
        result = self._make_metadata_request(meta_id=0, metadata_type='METADATA-RESOURCE')
        if resource:
            result = next((item for item in result if item['ResourceID'] == resource), None)
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
        Get the Metadata. The Session initializes with 'COMPACT-DECODED' as the format type. If that returns a DTD error
        then we change to the 'STANDARD-XML' format and try again.
        :param meta_id: The name of the resource, class, or lookup to get metadata for
        :param metadata_type: The RETS metadata type
        :return: list
        """
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
                        'Format': self.metadata_format
                    }
                }
            )
            self.metadata_responses[key] = response

        if self.metadata_format == 'COMPACT-DECODED':
            parser = CompactMetadata()
        else:
            parser = StandardXMLetadata()

        try:
            return parser.parse(response=response, metadata_type=metadata_type)
        except RETSException as e:
            # Remove response from cache
            self.metadata_responses.pop(key, None)

            # If the server responds with an invalid parameter for COMPACT-DECODED, try STANDARD-XML
            if self.metadata_format != 'STANDARD-XML' and e.reply_code in ['20513', '20514']:
                self.metadata_responses.pop(key, None)
                self.metadata_format = 'STANDARD-XML'
                return self._make_metadata_request(meta_id=meta_id, metadata_type=metadata_type)
            raise RETSException(e.reply_text, e.reply_code)

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
            collection = parser.parse_image_response(response)
        else:
            parser = SingleObjectParser()
            collection = [parser.parse_image_response(response)]

        return collection

    def search(self, resource, resource_class, search_filter=None, dmql_query=None, limit=9999999, offset=0,
               optional_parameters=None, auto_offset=True):
        """
        Preform a search on the RETS board
        :param resource: The resource that contains the class to search
        :param resource_class: The class to search
        :param search_filter: The query as a dict
        :param dmql_query: The query in dmql format
        :param limit: Limit search values count
        :param offset: Offset for RETS request. Useful when RETS limits number of results or transactions
        :param optional_parameters: Values for option paramters
        :param auto_offset: Should the search be allowed to trigger subsequent searches.
        :return: dict
        """

        if (search_filter and dmql_query) or (not search_filter and not dmql_query):
            raise ValueError("You may specify either a search_filter or dmql_query")

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
        if 'Select' in parameters and isinstance(parameters.get('Select'), list):
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
        try:
            return search_cursor.generator(response=response)

        except MaxrowException as max_exception:
            # Recursive searching if automatically performing offsets for the  client
            if auto_offset and limit > len(max_exception.rows_returned):
                new_limit = limit - len(max_exception.rows_returned)  # have not returned results to the desired limit
                new_offset = offset + len(max_exception.rows_returned)  # adjust offset
                results = self.search(resource=resource, resource_class=resource_class, search_filter=None,
                                      dmql_query=dmql_query, offset=new_offset, limit=new_limit,
                                      optional_parameters=optional_parameters, auto_offset=auto_offset)

                previous_results = max_exception.rows_returned
                return previous_results + results
            return max_exception.rows_returned

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
            msg = "{0!s} tried but no valid endpoints was found. Did you forget to Login?".format(capability)
            raise NotLoggedIn(msg)

        if self.user_agent_password:
            ua_digest = self._user_agent_digest_hash()
            options['headers']['RETS-UA-Authorization'] = 'Digest {0!s}'.format(ua_digest)

        if self.use_post_method and capability != 'Action':  # Action Requests should always be GET
            query = options.get('query')
            response = self.client.post(url, data=query, headers=options['headers'], stream=stream)
        else:
            if 'query' in options:
                url += '?' + '&'.join('{0!s}={1!s}'.format(k, quote(str(v))) for k, v in options['query'].items())

            response = self.client.get(url, headers=options['headers'], stream=stream)

        if response.status_code in [400, 401]:
            if capability == 'Login':
                m = "Could not log into the RETS server with the provided credentials."
            else:
                m = "The RETS server returned a 401 status code. You must be logged in to make this request."
            raise NotLoggedIn(m)

        elif response.status_code == 404 and self.use_post_method:
            raise HTTPException("Got a 404 when making a POST request. Try setting use_post_method=False when "
                                "initializing the Session.")

        return response

    def _user_agent_digest_hash(self):
        """
        Hash the user agent and user agent password
        Section 3.10 of https://www.nar.realtor/retsorg.nsf/retsproto1.7d6.pdf
        :return: md5
        """
        if not self.version:
            raise MissingVersion("A version is required for user agent auth. The RETS server should set this"
                                 "automatically but it has not. Please instantiate the session with a version argument"
                                 "to provide the version.")
        version_number = self.version.strip('RETS/')
        user_str = '{0!s}:{1!s}'.format(self.user_agent, self.user_agent_password).encode('utf-8')
        a1 = hashlib.md5(user_str).hexdigest()
        session_id = self.session_id if self.session_id is not None else ''
        digest_str = '{0!s}::{1!s}:{2!s}'.format(a1, session_id, version_number).encode('utf-8')
        digest = hashlib.md5(digest_str).hexdigest()
        return digest
