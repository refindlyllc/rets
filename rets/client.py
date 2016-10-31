import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from exceptions import RETSException
from resource import Resource
from parser import single_tier_xml_to_dict
import xml.etree.ElementTree as ET



class RETSClient(object):
    transactions = {}  # k/v of transactions and URLs, set during login()

    required_transactions = ['Login', 'Logout', 'Search', 'GetMetadata']
    available_transactions = required_transactions + ['Action', 'ChangePassword', 'GetObject', 'LoginComplete',
                             'ServerInformation', 'Update', 'PostObject', 'GetPayloadList']

    resources = []  # List of Resource Objects
    session = requests.Session()

    def __init__(self, login_url, rets_version, username, password, user_agent='REfindly RETS',
                 user_agent_password='', concurrent_sessions=1, auth_method='digest'):
        """
        Initialize the RETS Client with login credentials
        """
        self.login_url = login_url
        self.user_agent_password = user_agent_password
        self.concurrent_sessions = concurrent_sessions

        if auth_method in ['basic', 'digest']:
            if auth_method == 'basic':
                self.auth = HTTPBasicAuth(username, password)
            else:
                self.auth = HTTPDigestAuth(username, password)
        else:
            raise RETSException("auth_method must be either basic or digest for the RETS Client.")

        self.session_headers = {
            'User-Agent': user_agent,
            'RETS-Version': rets_version,
            'Accept-Encoding': 'gzip',
            'Accept': '*/*'
        }

        self.login(login_url)
        self.set_resources()
        print("hi")

    def rets_request(self, url):
        res = self.session.get(url,
                               auth=self.auth,
                               headers=self.session_headers
                               )

        return res

    def login(self, url):
        """
        Login to the rets server and verify that a 200 is returned. Get a session cookie.
        :return:
        """
        res = self.rets_request(url)

        if res.status_code != 200:
            raise RETSException("Could not log into RETS Client")

        # Set available transactions for this RETS
        res_text = res.text
        for line in res_text.split('\n'):
            if any(transaction in line for transaction in self.available_transactions):
                k, v = line.split('=', 1)
                self.transactions[k] = v.strip()

        if not all(transaction in self.transactions.keys() for transaction in self.required_transactions):
            raise RETSException("Could not get required transaction types from this RETS."
                                           "Need %s but have %s" % (self.required_transactions, self.transactions.keys()))

    def set_resources(self):
        print("Setting metadata, this may take a moment")
        metadata_url = self.transactions['GetMetadata'] + '?Type=METADATA-RESOURCE&ID=0'
        res = self.rets_request(url=metadata_url)
        if res.status_code != 200:
            raise RETSException("Could not get RETS Metadata")

        # Set Resources
        resource_dicts = single_tier_xml_to_dict(res.text)
        client_resources = []
        for resource_d in resource_dicts:
            client_resources.append(Resource(client=self, fields=resource_d))

        self.resources = client_resources


    def get_properties(self):
        """
        Get the available properties for an MLS and return the Property objects.
        :return:
        """
        return []

    def filter_to_dqml(self):
        pass


class ResultCursor(object):
    """
    An iterator. Keeps a search on hand and executes the results to a search and yields them when looped through


    Results can be stremed through requests http://docs.python-requests.org/en/latest/user/advanced/#body-content-workflow
    """
    count = 0

    def __init__(self, dqml_query, limit, etc):
        self.dqml_query = dqml_query
        self.limit = limit
        self.etc = etc

    def __len__(self):
        return self.count

    def get_result(self):
        """
        stream a record, up the count.
        :return:
        """
        pass


class Result(object):
    """
    Results yielded by the ResultCursor
    """

    def __repr__(self):
        return "This is a result"