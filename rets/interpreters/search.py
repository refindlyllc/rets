from rets.exceptions import InvalidSearch
import datetime
from time import time


class Search(object):

    @staticmethod
    def dmql(query):
        # automatically surround the given query with parentheses if it doesn't have them already
        if len(query) > 0 and query != "*" and query[0] != '(' and query[-1] != ')':
            query = '({})'.format(query)
        return query

    @staticmethod
    def filter_to_dmql(filter_dict):

        def evaluate_possible_datetimes(val):
            date_format = '%Y-%m-%d'
            time_format = '%H:%M:%S'

            if type(val) is datetime.datetime:
                evaluated = val.isoformat()
            elif type(val) is datetime.date:
                evaluated = val.strftime(date_format)
            elif type(val) is datetime.time:
                evaluated = val.strftime(time_format)
            else:
                evaluated = val

            return evaluated

        def evaluate_operators(key, val):
            allowed_operators = ['gte', 'lte', 'contains', 'begins', 'ends', 'or', 'in', 'nin', 'neq']
            evaluated = ''

            # If key not in allowed_operators, assume it is a field name with the and operation.


            for op, val in value.items():
                if op not in allowed_operators:
                    raise InvalidSearch("The supplied operator is not allowed. Please use: {}".
                                        format(allowed_operators))

                if type(value) is dict:
                    evaluated += evaluate_operator()
            return evaluated

        dmql_string = ''

        for filt, value in filter_dict.items():
            if type(value) is dict:
                # Applying an operator. This will need to be recursive because of the or possibility
                dmql_string += evaluate_operator(filt,value)
            else:
                value = evaluate_possible_datetimes(value)
                dmql_string += '({}={})'.format(filt, value)
        # Converts the filter dictionary to dmqp string
        print("Filter returned the following DMQL: {}".format(dmql_string))
        return dmql_string


        # between (listPrice=150000-200000)
        # greater than (listPrice=150000+)
        # less than (listPrice=200000-)
        # in (status=active,pending)
        # starts (status=act*)
        # ends (status=*ive)
        # contains (status=a*e)
        # in list (or operator) (status=A,P)
        # or between values |((status=A),(TaxYear=2016))
        # not in list (status=~A,P)
        # not equal (status=~A)
