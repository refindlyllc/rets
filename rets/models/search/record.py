

class Record(object):

    def __init__(self):
        self.parent = None
        self.record_key = None
        self.record_val = None
        self.values = {}

    def __repr__(self):
        return '<Record {} - {}:{}'.format(self.parent, self.record_key, self.record_val)

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
