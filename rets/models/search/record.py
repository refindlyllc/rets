

class Record(object):

    def __init__(self):
        self.parent = None
        self._record_key = None
        self.record_val = None
        self.values = {}

    def __repr__(self):
        return '<Record {}:{}>'.format(self.record_key, self.record_val)

    def get(self, key):
        return self.values.get(key, None)

    def set(self, key, val):
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
