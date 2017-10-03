import re

import xmltodict

from rets.parsers.base import Base


class OneXLogin(Base):

    def __init__(self):
        """Login Parser"""
        self.capabilities = {}
        self.details = {}
        self.headers = {}
        self.valid_transactions = [
            'Action', 'ChangePassword', 'GetObject', 'Login', 'LoginComplete', 'Logout', 'Search', 'GetMetadata',
            'ServerInformation', 'Update', 'PostObject', 'GetPayloadList'
        ]

    def parse(self, response):
        """
        Parse the login xml response
        :param response: the login response from the RETS server
        :return: None
        """
        self.headers = response.headers

        if 'xml' in self.headers.get('Content-Type'):
            # Got an XML response, likely an error code.
            xml = xmltodict.parse(response.text)
            self.analyze_reply_code(xml_response_dict=xml)

        lines = response.text.split('\r\n')
        if len(lines) < 3:
            lines = response.text.split('\n')

        for line in lines:
            line = line.strip()

            name, value = self.read_line(line)
            if name:
                if name in self.valid_transactions or re.match(pattern='/^X\-/', string=name):
                    self.capabilities[name] = value
                else:
                    self.details[name] = value

    @staticmethod
    def read_line(line):
        """Reads lines of XML and delimits, strips, and returns."""
        name, value = '', ''

        if '=' in line:
            name, value = line.split('=', 1)

        return [name.strip(), value.strip()]
