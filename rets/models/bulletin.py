

class Bulletin(object):
    body = None
    details = {}

    def __init__(self, details):
        if type(details) is dict:
            self.details = {k.upper(): v for k, v in details.items()}

    @property
    def member_name(self):
        return self.details.get('MemberName', None)

    @property
    def user(self):
        return self.details.get('User', None)

    @property
    def broker(self):
        return self.details.get('Broker', None)

    @property
    def metadata_version(self):
        return self.details.get('MetadataVersion', None)

    @property
    def metadata_timestamp(self):
        return self.details.get('MetadataTimestamp', None)

    