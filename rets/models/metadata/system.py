from .base_model import BaseModel


class SystemModel(BaseModel):

    def __init__(self, elements=None, attributes=None):
        self.SystemID = None
        self.SystemDescription = None
        self.TimeZoneOffset = None
        self.Comments = None
        self.Version = None
        self.load_elements_and_attributes(elements=elements, attributes=attributes)

    def __repr__(self):
        return '<System Metadata: {}>'.format(self.key)

    @property
    def key(self):
        return self.SystemID
