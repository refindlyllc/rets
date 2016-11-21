

class Base(object):

    def __init__(self, session):
        self.session = session

    @staticmethod
    def get_attributes(input_dict):
        return {k.lstrip('@'): v for k, v in input_dict.items() if k[0] == '@'}
