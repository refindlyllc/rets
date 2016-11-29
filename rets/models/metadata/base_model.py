

class BaseModel(object):
    """
    Base metadata class
    """
    attribute_keys = None
    element_keys = None

    def load_elements_and_attributes(self, elements=None, attributes=None):

        def set_attr_from_dict(source_dict):
            for k, v in source_dict.items():
                if hasattr(self, k):
                    setattr(self, k, v)

        if not attributes:
            attributes = {}
        if not elements:
            elements = {}

        set_attr_from_dict(attributes)
        self.attribute_keys = list(attributes.keys())
        set_attr_from_dict(elements)
        self.element_keys = list(elements.keys())
