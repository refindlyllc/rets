from .base_model import BaseModel


class SystemModel(BaseModel):

    def __repr__(self):
        return '<System Metadata: {}>'.format(self.SystemID)

    def __init__(self, elements=None, attributes=None):
        self.SystemID = None
        self.SystemDescription = None
        self.TimeZoneOffset = None
        self.Comments = None
        self.Version = None
        self.load_elements_and_attributes(elements=elements, attributes=attributes)
