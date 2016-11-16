import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from rets.exceptions import MissingConfiguration, CapabilityUnavailable
import logging
from rets.capabilities import Capabilities


class Session(object):

    logger = logging.getLogger(__name__)
    rets_session_id = None
    follow_redirecst = True
    capabilities = Capabilities()
    last_request_url = None
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
            'RETS-Version': self.configuration.rets_version,
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

        parser = self.grab('parser.login')

    def get_preferred_object(self):
        pass

    def get_object(self):
        pass

    def get_system_metadata(self):
        pass

    def get_resources_metadata(self):
        pass

    def get_classes_metadata(self):
        pass

    def get_table_metadata(self):
        pass

    def get_object_metadata(self):
        pass

    def get_lookup_values(self):
        pass

    def make_metadata_request(self):
        pass

    def search(self):
        pass

    def disconnect(self):
        pass

    def request(self, capability, options=None):
        if options is None:
            options = {
                'headers': self.client.headers.copy()
            }

        url = self.capabilities.capabilities.get(capability)

        if not url:
            raise CapabilityUnavailable("{} tried but no valid endpoints was found. Did you forget to Login()".format(capability))

        if self.configuration.user_agent_password:
            ua_digest = self.configuration.user_agent_digest_hash(self)
            options['headers']['RETS-UA-Authorization'] = 'Digest {}'.format(ua_digest)

        print("Sending HTTP Request for {}".format(capability))

        if 'query' in options:
            self.last_request_url = url + '?' + '&'.join('{}={}'.format(k, v) for k, v in options['query'].items())
        else:
            self.last_request_url = url

        if self.configuration.options.get('use_post_method'):
            print('Using POST method per use_post_method option')
            query = options.get('query')
            response = self.client.post(url, data=query, headers=options['headers'])
        else:
            response = self.client.get(url, headers=options['headers'])

        print("Response: HTTP {}".format(response.status_code))
        return response

    def get_login_url(self):
        pass

    def get_capabilities(self):
        pass

    def get_configuration(self):
        pass

    def get_last_request_url(self):
        pass

    def grab(self, component):
        return self.configuration.strategy.provide(component)
