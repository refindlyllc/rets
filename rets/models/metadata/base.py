

class Base(object):
    """
    Base metadata class
    """
    elements = {}
    attributes = {}
    values = {}

    def __init__(self, session, elements=None, attributes=None):
        self.session = session
        if elements:
            self.load_elements_and_attributes(elements=elements, attributes=attributes)

    def load_elements_and_attributes(self, elements, attributes=None):
        for attr in self.attributes:
            if attr in attributes:
                self.attributes[attr] = attributes[attr]

        for elem in self.elements:
            if elem in elements:
                self.elements[elem] = elements[elem]
