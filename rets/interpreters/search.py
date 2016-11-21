import re


class Search(object):

    @staticmethod
    def dmqp(query):
        # automatically surround the given query with parentheses if it doesn't have them already
        if len(query) > 0 and query != "*" and query[0] != '(' and query[-1] != ')':
            query = '({})'.format(query)
        return query

    @staticmethod
    def filter_to_dmqp(filter_dict):

        date_format = 'YYYY-MM-DD'
        time_format = 'HH:MM:SS'
        datetime_format = 'YYYY-MM-DDTHH:MM:SS'

        allowed_operators = ['gt', 'gte', 'lt', 'lte', 'contains', 'begins', 'ends', 'or']



        # Converts the filter dictionary to dmqp string
        pass
