

class OneX(object):
    capabilities = []
    details = {}
    valid_transactions = [
        'Action', 'ChangePassword', 'GetObject', 'Login', 'LoginComplete', 'Logout', 'Search', 'GetMetadata',
        'ServerInformation', 'Update', 'PostObject', 'GetPayloadList'
    ]

    @staticmethod
    def parse(body):
        lines = body.split('\r\n')
        if len(lines) < 3:
            lines = body.split('\n')

    @staticmethod
    def read_line(line):
        pass
