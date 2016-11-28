from .base import Base


class LookupTypeModel(Base):
    elements = {
        'MetadataEntryID': None,
        'LongValue': None,
        'ShortValue': None,
        'Value': None,
    }
    attributes = {
        'Version': None,
        'Date': None,
        'Resource': None,
        'Lookup': None,
    }

    def __repr__(self):
        return '<Lookup Type Metadata: {}>'.format(self.elements['ShortValue'])