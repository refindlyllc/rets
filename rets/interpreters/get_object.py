import re


class GetObject(object):

    def ids(self, content_ids, object_ids):
        result = []

        content_ids = self.split(content_ids, False)
        object_ids = self.split(object_ids)

        for cid in content_ids:
            # https://github.com/troydavisson/PHRETS/blob/master/src/Interpreters/GetObject.php#L19
            # do this
            result

        return result

    @staticmethod
    def split(value, dash_ranges=True):

        if type(value) is not list:
            if re.match(pattern='/\:/', string=value) or re.match(pattern='/\,/', string=value):
                value = [v.strip() for v in value.split(':')]
            elif dash_ranges:
                matches = re.match(pattern='/(\d+)\-(\d+)/', string=value)
                value = range(matches.group(1), matches.group(2))
            else:
                value = [value]

        return value
