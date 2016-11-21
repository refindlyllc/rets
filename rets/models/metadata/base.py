

class Base(object):
    """
    Base metadata class
    """
    elements = {}
    attributes = {}
    values = {}

    def __init__(self, session):
        self.session = session
