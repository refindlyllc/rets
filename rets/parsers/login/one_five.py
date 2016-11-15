from rets.parsers.login.one_x import OneX


class OneFive(OneX):

    @staticmethod
    def read_line(line):
        name, value = None, None

        if '=' in line:
            name, value = line.split('=', 1)
        return [name.strip(), value.strip()]
