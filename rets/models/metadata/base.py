

class Base(object):
    """
    Base metadata class
    """
    elements = {}
    attributes = {}
    values = {}

    def __init__(self, elements=None, attributes=None):
        if attributes:
            for attr in self.attributes:
                if attr in attributes:
                    self.attributes[attr] = attributes[attr]
        if elements:
            for elem in self.elements:
                if elem in elements:
                    self.elements[elem] = elements[elem]
