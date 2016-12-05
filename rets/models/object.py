

class Object(object):

    def __init__(self):
        self.content_type = None
        self.content_id = None
        self.object_id = None
        self.mime_version = None
        self.location = None
        self.content_description = None
        self.content_sub_description = None
        self.content = []
        self.preferred = None
        self.error = None

    def __len__(self):
        return len(self.content)

    def is_preferred(self):
        if self.preferred == 1:
            return True
        return False

    def is_error(self):
        if self.error:
            return True
        return False
