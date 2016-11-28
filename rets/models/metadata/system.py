from .base import Base


class SystemModel(Base):
    elements = {
        'SystemID': None,
        'SystemDescription': None,
        'TimeZoneOffset': None,
        'Comments': None,
        'Version': None,
    }

    def __repr__(self):
        return '<System Metadata: {}>'.format(self.elements['SystemID'])
