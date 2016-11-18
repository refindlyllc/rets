from rets.models.metadata.base import Base


class ResourceClass(Base):
    resource = None
    elements = {
        'ClassName': None,
        'VisibleName': None,
        'StandardName': None,
        'Description': None,
        'TableVersion': None,
        'TableDate': None,
        'UpdateVersion': None,
        'UpdateDate': None,
        'ClassTimeStamp': None,
        'DeletedFlagField': None,
        'DeletedFlagValue': None,
        'HasKeyIndex': None,
    }
    attributes = {
        'Version': None,
        'Date': None,
        'Resource': None,
    }

    def __init__(self, resource):
        self.resource = resource

    def get_table(self):
        return self.session.get_table_metadata(self.resource, self.classname)