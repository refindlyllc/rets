from .base import Base


class ResourceModel(Base):
    """
    metadata resource
    """

    attributes = {
        'Version': None,
        'Date': None,
    }

    classes = None
    objects = None

    def __init__(self, *args, **kwargs):
        super(ResourceModel, self).__init__(*args, **kwargs)
        self.elements = {
            'ResourceID': None,
            'StandardName': None,
            'VisibleName': None,
            'Description': None,
            'KeyField': None,
            'ClassCount': None,
            'ClassVersion': None,
            'ClassDate': None,
            'ObjectVersion': None,
            'ObjectDate': None,
            'SearchHelpVersion': None,
            'SearchHelpDate': None,
            'EditMaskVersion': None,
            'EditMaskDate': None,
            'LookupVersion': None,
            'LookupDate': None,
            'UpdateHelpVersion': None,
            'UpdateHelpDate': None,
            'ValidationExpressionVersion': None,
            'ValidationExpressionDate': None,
            'ValidationLookupVersion': None,
            'ValidationLookupDate': None,
            'ValidationExternalVersion': None,
            'ValidationExternalDate': None,
        }

    @property
    def key(self):
        return self.elements['KeyField']

    @property
    def resource_id(self):
        return self.elements['ResourceID']
