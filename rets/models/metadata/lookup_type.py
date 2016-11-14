from rets.models.metadata.base import Base


class LookupType(Base):
    elements = [
        'MetadataEntryID',
        'LongValue',
        'ShortValue',
        'Value',
    ]
    attributes = [
        'Version',
        'Date',
        'Resource',
        'Lookup',
    ]
