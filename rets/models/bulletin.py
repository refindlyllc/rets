

class Bulletin(object):
    body = None
    details = {}

    def __init__(self, details):
        if type(details) is dict:
            self.details = details

    @property
    def member_name(self):
        return self.details.get('MemberName', None)

    @member_name.setter
    def member_name(self, val):
        self.details['MemberName'] = val

    @property
    def user(self):
        return self.details.get('User', None)

    @user.setter
    def user(self, val):
        self.details['User'] = val

    @property
    def broker(self):
        return self.details.get('Broker', None)

    @broker.setter
    def broker(self, val):
        self.details['Broker'] = val

    @property
    def metadata_version(self):
        return self.details.get('MetadataVersion', None)

    @metadata_version.setter
    def metadata_version(self, val):
        self.details['MetadataVersion'] = val

    @property
    def metadata_timestamp(self):
        return self.details.get('MetadataTimestamp', None)

    @metadata_timestamp.setter
    def metadata_timestamp(self, val):
        self.details['MetadataTimestamp'] = val
