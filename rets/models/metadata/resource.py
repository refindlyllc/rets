from .base import Base


class ResourceModel(Base):
    """
    metadata resource
    """
    elements = {
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
    attributes = {
        'Version': None,
        'Date': None,
    }

    classes = None
    objects = None

    def __repr__(self):
        return '<Resource Metadata: {}>'.format(self.elements['ResourceID'])

    @property
    def key(self):
        return self.elements['KeyField']

    @property
    def resource_id(self):
        return self.elements['ResourceID']

    def get_classes(self):
        if not self.classes:
            self.classes = self.session.get_classes_metadata()
        return self.classes

    def get_objects(self):
        if not self.objects:
            self.objects = self.session.get_object_metadata()
        return self.objects
