from rets.models.metadata.base import Base


class Resource(Base):
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

    def get_classes(self):
        return self.session.get_classes_metadata()

    def get_object(self):
        return self.session.get_object_metadata()
