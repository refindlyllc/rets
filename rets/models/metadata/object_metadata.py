from .base_model import BaseModel


class ObjectMetadataModel(BaseModel):

    def __repr__(self):
        return '<Object Metadata: {}>'.format(self.VisibleName)
    
    def __init__(self, elements=None, attributes=None):
        self.MetadataEntryID = None
        self.VisibleName = None
        self.ObjectTimeStamp = None
        self.ObjectCount = None
        self.ObjectType = None
        self.StandardName = None
        self.MIMEType = None
        self.Description = None
        self.Version = None
        self.Date = None
        self.Resource = None

        self.load_elements_and_attributes(elements=elements, attributes=attributes)
