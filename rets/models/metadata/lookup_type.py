from rets.models.metadata.base import Base


class LookupType(Base):
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