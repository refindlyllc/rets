

class Object(object):
    content_type = None
    content_id = None
    object_id = None
    mime_version = None
    location = None
    content_description = None
    content_sub_description = None
    content = []
    preferred = None
    error = None

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
