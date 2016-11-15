import xmltodict
from rets.exceptions import RETSException


class Resource(object):
    """
    The Resource object knows about itself and its classes
    """
    _classes = None
    _lookups = {}
    ResourceID = ''

    def __init__(self, client, fields=None):
        self.client = client
        if fields is None:
            self.fields = {}
        else:
            self.fields = fields
        self.ResourceID = fields.get('ResourceID')

    def _set_classes(self):
        """
        Get the classes beloging to this property
        :return: list
        """
        class_url = self.client.transactions['GetMetadata'] + '?Type=METADATA-CLASS&ID=' + self.ResourceID
        res = self.client.rets_request(class_url)
        res_dict = xmltodict.parse(res.text)

        resource_classes = []
        for class_dict in res_dict:
            r_class = ResourceClass(resource=self, class_dict=class_dict)
            resource_classes.append(r_class)

        self._classes = resource_classes
        return resource_classes

    @property
    def classes(self):
        if self._classes is not None:
            return self._classes
        else:
            return self._set_classes()

    @property
    def lookups(self):
        return self._lookups

    @lookups.getter
    def get_lookup(self, lookup_short_name):
        if lookup_short_name not in self._lookups:
            # Get the lookup
            pass
        else:
            lookup_val = self._lookups.get(lookup_short_name)
            if lookup_val is None:
                raise RETSException("%s is not a valid lookup value" % lookup_short_name)
            return lookup_val


class ResourceClass(object):
    """
    The class belonging to a resource. It knows about its fields.
    """
    num_fields = 0
    key_field = None
    class_name = ''
    class_fields = None

    def __init__(self, resource, class_dict):
        self.resource = resource
        self.set_fields()

    @property
    def fields(self):
        if self.class_fields is not None:
            return self.class_fields
        else:
            return self.set_fields()

    def set_fields(self):
        fields_url = self.resource.client.transactions['GetMetadata'] + '?Type=METADATA-TABLE&ID=' + self.resource.ResourceID + ":" + self.class_name
        res = self.resource.client.rets_request(fields_url)

        class_fields = xmltodict.parse(res.text)
        fields = []
        for class_dict in class_fields:
            class_field = ClassField(resource_class=self, fields=class_dict)
            fields.append(class_field)

        self.class_fields = fields
        return fields




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

        lookups = xmltodict.parse(res.text)
        lookup_dicts = []
        for lookup_dict in lookups:
            field_lookup = FieldLookup(class_field=self, fields=lookup_dict)
            lookup_dicts.append(field_lookup)
        self.lookup_values = lookup_dicts

class FieldLookup(object):
    """
    The lookup is possible values for a given field. This is shared across properties.
    """
    metadata_entry_id = None
    long_value = None
    short_value = None
    value = None
    class_field = None  # The ClassField of this lookupg

    def __init__(self, class_field):
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