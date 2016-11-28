from .base import Base


class ResourceClassModel(Base):
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

    table = None

    def __init__(self, resource, *args, **kwargs):
        super(ResourceClassModel, self).__init__(*args, **kwargs)
        self.resource = resource

    def __repr__(self):
        return '<Class Metadata: {}>'.format(self.class_name)

    @property
    def class_name(self):
        return self.elements['ClassName']

    def get_table(self):
        if not self.table:
            self.table = self.session.get_table_metadata(self.resource, self.class_name)
        return self.table