from .base_model import BaseModel


class ResourceModel(BaseModel):
    """
    metadata resource
    """
    def __repr__(self):
        return '<Resource Metadata: {}>'.format(self.ResourceID)

    def __init__(self, elements=None, attributes=None):
        self.Version = None
        self.Date = None

        self.ResourceID = None
        self.StandardName = None
        self.VisibleName = None
        self.Description = None
        self.KeyField = None
        self.ClassCount = None
        self.ClassVersion = None
        self.ClassDate = None
        self.ObjectVersion = None
        self.ObjectDate = None
        self.SearchHelpVersion = None
        self.SearchHelpDate = None
        self.EditMaskVersion = None
        self.EditMaskDate = None
        self.LookupVersion = None
        self.LookupDate = None
        self.UpdateHelpVersion = None
        self.UpdateHelpDate = None
        self.ValidationExpressionVersion = None
        self.ValidationExpressionDate = None
        self.ValidationLookupVersion = None
        self.ValidationLookupDate = None
        self.ValidationExternalVersion = None
        self.ValidationExternalDate = None

        self.load_elements_and_attributes(elements=elements, attributes=attributes)
