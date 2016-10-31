class Resource(object):
    """
    The property object knows about itself and its classes
    """
    classes = []

    def __init__(self):
        self.classes = self.get_classes()

    def get_classes(self):
        """
        Get the classes beloging to this property
        :return: list
        """
        return []


class ResourceClass(object):
    """
    The class belonging to a resource
    """
    num_fields = None
    key_field = None


class ClassField(object):
    """
    The field itself
    """
    pass


class FieldLookup(object):
    """
    The lookup value possible for a given field
    """
    metadata_entry_id = None
    long_value = None
    short_value = None
    value = None
    parent_class = None  # The ClassField of this lookupg


class ClassObjects(object):
    """
    The objects of a given class
    """
    standard_name = None
    visible_name = None
    mime_type = None
    description = None
    metadata_entry_id = None
    object_time_stamp = None
    object_count = None
    object_type = None
    parent_class = None  # parent ResourceClass


class Metadata(object):
    """
    The metadata for the MLS Board
    """