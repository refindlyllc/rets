import xml.etree.ElementTree as ET


class Resource(object):
    """
    The property object knows about itself and its classes
    """
    classes = []
    ResourceID = ''

    def __init__(self, client, fields={}):
        self.client = client
        self.fields = fields
        self.ResourceID = fields['ResourceID']
        self.set_classes()

    def set_classes(self):
        """
        Get the classes beloging to this property
        :return: list
        """
        class_url = self.client.transactions['GetMetadata'] + '?Type=METADATA-CLASS&ID=' + self.ResourceID
        res = self.client.rets_request(class_url)

        root = ET.fromstring(res.text)

        classes = root[0][0]

        # Set Classes
        for c in classes:
            fields = {field.tag: field.text for field in c}
            r_class = ResourceClass(fields=fields)
            self.classes.append(r_class)


class ResourceClass(object):
    """
    The class belonging to a resource
    """
    num_fields = 0
    key_field = None

    def __init__(self, fields={}):
        self.fields = fields


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


class ClassObject(object):
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