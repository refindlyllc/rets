import re
from rets.parsers.base import Base


class OneXLogin(Base):
    capabilities = {}
    details = {}
    headers = {}
    valid_transactions = [
        'Action', 'ChangePassword', 'GetObject', 'Login', 'LoginComplete', 'Logout', 'Search', 'GetMetadata',
        'ServerInformation', 'Update', 'PostObject', 'GetPayloadList'
    ]

    def parse(self, body):
        """
        Parse the login xml response
        :param body: the login XML
        :return: None
        """
        lines = body.split('\r\n')
        if len(lines) < 3:
            lines = body.split('\n')

        for line in lines:
            lines = line.strip()
            if not line:
                continue

            name, value = self.read_line(line)
            if name:
                if name in self.valid_transactions or re.match(pattern='/^X\-/', string=name):
                    self.capabilities[name] = value
                else:
                    self.details[name] = value

    def parse_headers(self, headers):
        """
        Parse the heads to extract useful information
        :param headers: The headers given in the response
        :return:
        """
        if headers.get('RETS-Version', None):
            self.headers['RETS-Version'] = headers.get('RETS-Version').strip('RETS/')

    @staticmethod
    def read_line(line):
        pass
