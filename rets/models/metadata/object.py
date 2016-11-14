from rets.models.metadata.base import Base


class Object(Base):
    elements = [
        'MetadataEntryID',
        'VisibleName',
        'ObjectTimeStamp',
        'ObjectCount',
        'ObjectType',
        'StandardName',
        'MIMEType',
        'Description',
    ]
    attributes = [
        'Version',
        'Date',
        'Resource',
    ]