

class Base(object):

    @staticmethod
    def get_attributes(input_dict):
        return {k.lstrip('@'): v for k, v in input_dict.items() if k[0] == '@'}

    @staticmethod
    def data_columns_to_dict(columns_string, dict_string):
        return {k: v for k, v in zip(columns_string.split(), dict_string.split())}
