

class Record(object):
    parent = None
    values = {}

    def get(self, key):
        return self.values.get(key, None)

    def set(self, key, val):
        self.values[key] = val

    def is_restricted(self):
        # Not sure what this does
        # https://github.com/troydavisson/PHRETS/blob/b03c7f5f9f10bd4cdb77e5d13d8fdf6f50351222/src/Models/Search/Record.php#L31
        pass

    @property
    def resource(self):
        return self.parent.resource

    @property
    def resource_class(self):
        return self.parent.resource_class

    def get_images(self):
        # get the images for a records
        pass