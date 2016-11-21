from rets.models.metadata.base import Base


class Object(Base):
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
