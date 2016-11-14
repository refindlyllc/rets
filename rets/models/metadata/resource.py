from rets.models.metadata.base import Base


class Resource(Base):
    """
    metadata resource
    """
    elements = [
        'ResourceID',
        'StandardName',
        'VisibleName',
        'Description',
        'KeyField',
        'ClassCount',
        'ClassVersion',
        'ClassDate',
        'ObjectVersion',
        'ObjectDate',
        'SearchHelpVersion',
        'SearchHelpDate',
        'EditMaskVersion',
        'EditMaskDate',
        'LookupVersion',
        'LookupDate',
        'UpdateHelpVersion',
        'UpdateHelpDate',
        'ValidationExpressionVersion',
        'ValidationExpressionDate',
        'ValidationLookupVersion',
        'ValidationLookupDate',
        'ValidationExternalVersion',
        'ValidationExternalDate',
    ]
    attributes = [
        'Version',
        'Date',
    ]

    def get_classes(self):
        return self.session.get_classes_metadata()

    def get_object(self):
        return self.session.get_object_metadata()
