

class Base(object):

    @staticmethod
    def get_attributes(input_dict):
        """
        Get attributes of xml tags in input_dict and creates a dictionary with the attribute name as the key and the
        attribute value as the value
        :param input_dict: The xml tag with the attributes and values
        :return: dict
        """
        return {k.lstrip('@'): v for k, v in input_dict.items() if k[0] == '@'}

    @staticmethod
    def data_columns_to_dict(columns_string, dict_string, delimiter=None):
        """
        Turns column names in a single string into a dictionary with the key being the column name and the value
        being the value in that column for each row
        :param columns_string: A string of column names
        :param dict_string: A string of values
        :param delimiter: The delimiter to use to split the column and values
        :return: dict
        """
        if delimiter:
            return {k: v for k, v in zip(columns_string.split(delimiter), dict_string.split(delimiter))}
        else:
            return {k: v for k, v in zip(columns_string.split(), dict_string.split())}
