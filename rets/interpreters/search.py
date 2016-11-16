import re


class Search(object):

    @staticmethod
    def dmqp(query):
        # automatically surround the given query with parentheses if it doesn't have them already
        if len(query) > 0 and query != "*" and not re.match(pattern='/^\((.*)\)$/', string=query):
            query = '({})'.format(query)
        return query
