import xml.etree.ElementTree as ET
from parser import single_tier_xml_to_dict


class Resource(object):
    """
    The Resource object knows about itself and its classes
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

        classes = single_tier_xml_to_dict(res.text)
        resource_classes = []
        for class_dict in classes:
            r_class = ResourceClass(resource=self, fields=class_dict)
            resource_classes.append(r_class)

        self.classes = resource_classes


class ResourceClass(object):
    """
    The class belonging to a resource. It knows about its fields.
    """
    num_fields = 0
    key_field = None
    class_name = ''

    def __init__(self, resource, fields={}):
        self.resource = resource
        self.fields = fields
        self.class_name = fields['ClassName']
        self.num_fields = len(fields)
        self.set_fields()

    def set_fields(self):
        fields_url = self.resource.client.transactions['GetMetadata'] + '?Type=METADATA-TABLE&ID=' + self.resource.ResourceID + ":" + self.class_name
        res = self.resource.client.rets_request(fields_url)

        classes = single_tier_xml_to_dict(res.text)
        fields = []
        for class_dict in classes:
            class_field = ClassField(resource_class=self, fields=class_dict)
            fields.append(class_field)

        self.fields = fields


class ClassField(object):
    """
    The field is data for a class. Some fields have a lookup.
    """
    def __init__(self, resource_class, fields={}):
        self.resource_class = resource_class
        self.fields = fields
        self.short_name = fields['ShortName']
        self.num_fields = len(fields)
        self.lookup_values = []

        if self.fields.get('LookupName', None) is not None:
            self.set_lookup()

    def set_lookup(self):
        lookup_url = self.resource_class.resource.client.transactions['GetMetadata'] + '?Type=METADATA-LOOKUP_TYPE&ID='\
                     + self.resource_class.resource.ResourceID + ":" + self.short_name
        res = self.resource_class.resource.client.rets_request(lookup_url)

        lookups = single_tier_xml_to_dict(res.text)
        lookup_dicts = []
        for lookup_dict in lookups:
            field_lookup = FieldLookup(class_field=self, fields=lookup_dict)
            lookup_dicts.append(field_lookup)
        self.lookup_values = lookup_dict

class FieldLookup(object):
    """
    The lookup is possible values for a given field. This is shared across properties.
    """
    metadata_entry_id = None
    long_value = None
    short_value = None
    value = None
    class_field = None  # The ClassField of this lookupg

    def __init__(self, class_field, fields={}):
        self.fields = fields
        self.class_field = class_field


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