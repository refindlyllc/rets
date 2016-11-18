import re


class GetObject(object):

    def ids(self, content_ids, object_ids):
        result = []

        content_ids = self.split(content_ids, False)
        object_ids = self.split(object_ids)

        for cid in content_ids:
            result.append('{}:{}'.format(cid, ':'.join(object_ids)))

        return result

    @staticmethod
    def split(value, dash_ranges=True):

        dash_matches = re.match(pattern='/(\d+)\-(\d+)/', string=value)
        if type(value) is not list:
            if re.match(pattern='/\:/', string=value) or re.match(pattern='/\,/', string=value):
                value = [v.strip() for v in value.split(':')]
            elif dash_ranges and dash_matches:
                value = range(dash_matches.group(1), dash_matches.group(2))
            else:
                value = [value]

        return value
