from rets.models.metadata.base import Base


class ResourceClass(Base):
    resource = None
    elements = [
        'ClassName',
        'VisibleName',
        'StandardName',
        'Description',
        'TableVersion',
        'TableDate',
        'UpdateVersion',
        'UpdateDate',
        'ClassTimeStamp',
        'DeletedFlagField',
        'DeletedFlagValue',
        'HasKeyIndex',
    ]
    attributes = [
        'Version',
        'Date',
        'Resource',
    ]

    def __init__(self, resource):
        self.resource = resource

    def get_table(self):
        return self.session.get_table_metadata(self.resource, self.classname)