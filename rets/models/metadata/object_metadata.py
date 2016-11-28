from .base import Base


class ObjectMetadataModel(Base):
    elements = {
        'MetadataEntryID': None,
        'VisibleName': None,
        'ObjectTimeStamp': None,
        'ObjectCount': None,
        'ObjectType': None,
        'StandardName': None,
        'MIMEType': None,
        'Description': None,
    }
    attributes = {
        'Version': None,
        'Date': None,
        'Resource': None,
    }

    def __repr__(self):
        return '<Object Metadata: {}>'.format(self.elements['VisibleName'])
