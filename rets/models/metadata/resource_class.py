from .base_model import BaseModel


class ResourceClassModel(BaseModel):

    def __init__(self, resource=None, elements=None, attributes=None):
        self.resource = resource

        self.ClassName = None
        self.VisibleName = None
        self.StandardName = None
        self.Description = None
        self.TableVersion = None
        self.TableDate = None
        self.UpdateVersion = None
        self.UpdateDate = None
        self.ClassTimeStamp = None
        self.DeletedFlagField = None
        self.DeletedFlagValue = None
        self.HasKeyIndex = None
        self.Version = None
        self.Date = None
        self.Resource = None

        self.load_elements_and_attributes(elements=elements, attributes=attributes)

    def __repr__(self):
        return '<Class Metadata: {}>'.format(self.class_name)

    @property
    def class_name(self):
        return self.ClassName
