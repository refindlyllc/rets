import re


class GetObject(object):
    """Handles various formatting for the GetObject metadata request"""

    def ids(self, content_ids, object_ids):
        """Appends the content and object ids how RETS expects them"""
        result = []

        content_ids = self.split(content_ids, False)
        object_ids = self.split(object_ids)

        for cid in content_ids:
            result.append('{}:{}'.format(cid, ':'.join(object_ids)))

        return result

    @staticmethod
    def split(value, dash_ranges=True):
        """Splits """
        if type(value) is list:
            value = [str(v) for v in value]
        else:
            str_value = str(value)
            dash_matches = re.match(pattern='(\d+)\-(\d+)', string=str_value)

            if ':' in str_value or ',' in str_value:
                value = [v.strip() for v in str_value.replace(',', ':').split(':')]
            elif dash_ranges and dash_matches:
                start_range = int(dash_matches.group(1))
                end_range = int(dash_matches.group(2)) + 1
                rng = range(start_range, end_range)
                value = [str(r) for r in rng]
            else:
                value = [str_value]

        return value
