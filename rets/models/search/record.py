

class Record(object):
    parent = None
    record_key = None
    record_val = None
    values = {}

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
        return self.parent.restricted_indicator == field

    @property
    def resource(self):
        return self.parent.resource

    @property
    def resource_class(self):
        return self.parent.resource_class

    def get_images(self):
        # get the images for a records
        pass
