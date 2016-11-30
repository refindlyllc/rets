from .one_x import OneXLogin


class OneFiveLogin(OneXLogin):

    @staticmethod
    def read_line(line):
        name, value = '', ''

        if '=' in line:
            name, value = line.split('=', 1)

        return [name.strip(), value.strip()]
