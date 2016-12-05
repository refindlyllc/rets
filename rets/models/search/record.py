

class Record(object):

    def __init__(self):
        self.parent = None
        self._record_key = None
        self.record_val = None
        self.values = {}

    def __repr__(self):
        return '<Record {}:{}>'.format(self.record_key, self.record_val)

    def get(self, key):
        """
        Get a value from the values attribute
        :param key: The key to use to get the value from values dict
        :return: The value associated with the key
        """
        return self.values.get(key, None)

    def set(self, key, val):
        """
        Set a key in the values attribute to the value of val.
        :param key: The key to look for in the values dictionary
        :param val: The value to assign to the key
        :return: None
        """
        if key == self.record_key:
            self.record_val = val
        self.values[key] = val

    def is_restricted(self, field):
        # Checks if this records field is the restricted indicator
        return self.parent.restricted_indicator == self.get(field)

    @property
    def resource(self):
        return self.parent.resource

    @property
    def resource_class(self):
        return self.parent.resource_class

    @property
    def record_key(self):
        if not self._record_key:
            self._record_key = self.parent.metadata.KeyField
        return self._record_key

    @record_key.setter
    def record_key(self, val):
        self._record_key = val
