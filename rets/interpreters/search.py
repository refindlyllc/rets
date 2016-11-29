from rets.exceptions import InvalidSearch
import datetime


class SearchInterpreter(object):

    @staticmethod
    def dmql(query):
        # automatically surround the given query with parentheses if it doesn't have them already
        if len(query) > 0 and query != "*" and query[0] != '(' and query[-1] != ')':
            query = '({})'.format(query)
        return query

    @staticmethod
    def filter_to_dmql(filter_dict):

        def is_date_time_type(val):
            return type(val) in [datetime.datetime, datetime.date, datetime.time]

        def evaluate_datetime(val):
            date_format = '%Y-%m-%d'
            time_format = '%H:%M:%S'
            datetime_format = '{}T{}'.format(date_format, time_format)

            if type(val) is datetime.datetime:
                evaluated = val.strftime(datetime_format)
            elif type(val) is datetime.date:
                evaluated = val.strftime(date_format)
            elif type(val) is datetime.time:
                evaluated = val.strftime(time_format)
            else:
                evaluated = val

            return evaluated

        def evaluate_operators(key_dict):
            allowed_operators = ['$gte', '$lte', '$contains', '$begins', '$ends', '$in', '$nin', '$neq']

            # If key not in allowed_operators, assume it is a field name with the and operation.
            if not all(op in allowed_operators for op in key_dict.keys()):
                raise InvalidSearch("You have supplied an invalid operator. "
                                    "Please provide one of the following {}".format(allowed_operators))

            # We can have a single operator key, or the combination of gte/lte
            keys = key_dict.keys()
            string = ''

            # Search between two numbers or two dates
            if len(keys) == 2 and all(k in ['$gte', '$lte'] for k in keys):
                if all(is_date_time_type(key_dict[v]) for v in keys):
                    # comparing dates
                    string = '{}-{}'.format(evaluate_datetime(key_dict['$gte']), evaluate_datetime(key_dict['$lte']))
                else:
                    # comparing numbers
                    try:
                        float(key_dict['$gte'])
                        float(key_dict['$lte'])
                    except ValueError:
                        raise InvalidSearch("$gte and $lte expect numeric or datetime values")
                    string = '{:.2f}-{:.2f}'.format(key_dict['$gte'], key_dict['$lte'])

            # Using a single operator key
            elif len(keys) == 1:
                if '$gte' in key_dict:
                    if is_date_time_type(key_dict['$gte']):
                        string = '{}+'.format(evaluate_datetime(key_dict['$gte']))
                    else:
                        try:
                            float(key_dict['$gte'])
                        except ValueError:
                            raise InvalidSearch("$gte expects a numeric value or a datetime object")
                        string = '{:.2f}+'.format(key_dict['$gte'])

                elif '$lte' in key_dict:
                    if is_date_time_type(key_dict['$lte']):
                        string = '{}-'.format(evaluate_datetime(key_dict['$lte']))
                    else:
                        try:
                            float(key_dict['$lte'])
                        except ValueError:
                            raise InvalidSearch("$lte expects a numeric value or a datetime object")
                        string = '{:.2f}-'.format(key_dict['$lte'])

                elif '$in' in key_dict:
                    if type(key_dict['$in']) is not list:
                        raise InvalidSearch("in expects a list of strings")
                    key_dict['$in'] = [evaluate_datetime(v) for v in key_dict['$in']]
                    if not all(type(v) is str for v in key_dict['$in']):
                        raise InvalidSearch("$in expects a list of strings")
                    options = ','.join(key_dict['$in'])
                    string = '{}'.format(options)

                elif '$nin' in key_dict:
                    if type(key_dict['$nin']) is not list:
                        raise InvalidSearch("$nin expects a list of strings")
                    key_dict['$nin'] = [evaluate_datetime(v) for v in key_dict['$nin']]
                    if not all(type(v) is str for v in key_dict['$nin']):
                        raise InvalidSearch("$nin expects a list of strings")
                    options = ','.join(key_dict['$nin'])
                    string = '~{}'.format(options)

                elif '$contains' in key_dict:
                    if type(key_dict['$contains']) is not str:
                        raise InvalidSearch("$contains expects a string.")
                    string = '*{}*'.format(key_dict['$contains'])

                elif '$begins' in key_dict:
                    if type(key_dict['$begins']) is not str:
                        raise InvalidSearch("$begins expects a string.")
                    string = '{}*'.format(key_dict['$begins'])

                elif '$ends' in key_dict:
                    if type(key_dict['$ends']) is not str:
                        raise InvalidSearch("$ends expects a string.")
                    string = '*{}'.format(key_dict['$ends'])

                elif '$neq' in key_dict:
                    string = '~{}'.format(key_dict['$neq'])

            else:
                # Provided too many or too few operators
                raise InvalidSearch("Please supply $gte and $lte for getting values between numbers or 1 of {}".format(
                    allowed_operators))

            return string

        dmql_search_filters = []

        for filt, value in filter_dict.items():
            dmql_string = '({}='.format(filt)
            if type(value) is dict:
                # Applying an operator. This will need to be recursive because of the or possibility
                dmql_string += evaluate_operators(key_dict=value)
            else:
                # Simle equals statement
                dmql_string += '{}'.format(evaluate_datetime(value))
            dmql_string += ')'
            dmql_search_filters.append(dmql_string)

        search_string = ','.join(dmql_search_filters)
        # Converts the filter dictionary to dmqp string
        print("Filter returned the following DMQL: {}".format(search_string))
        return search_string
