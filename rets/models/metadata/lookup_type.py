from .base_model import BaseModel


class LookupTypeModel(BaseModel):

    def __init__(self, elements=None, attributes=None):

        self.MetadataEntryID = None
        self.LongValue = None
        self.ShortValue = None
        self.Value = None
        self.Version = None
        self.Date = None
        self.Resource = None
        self.Lookup = None

        self.load_elements_and_attributes(elements=elements, attributes=attributes)

    def __repr__(self):
        return '<Lookup Type Metadata: {}>'.format(self.key)

    @property
    def key(self):
        return self.ShortValue
