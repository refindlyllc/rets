

class OneX(object):
    capabilities = []
    details = {}
    valid_transactions = [
        'Action', 'ChangePassword', 'GetObject', 'Login', 'LoginComplete', 'Logout', 'Search', 'GetMetadata',
        'ServerInformation', 'Update', 'PostObject', 'GetPayloadList'
    ]

    def parse(self, body):
        lines = body.split('\r\n')
        if len(lines) < 3:
            lines = body.split('\n')

    def read_line(self, line):
        pass
