from rets.parsers.login.one_x import OneX


class OneFive(OneX):

    @staticmethod
    def read_line(line):
        name, value = None, None

        if '=' in line:
            name, value = line.split('=', 1)

        if name == 'Info' and value is not None:
            name, d_type, value = value.split(';')
            if d_type == 'Int':
                value = int(value)
            elif d_type == 'Boolean':
                value = bool(value)
            else:
                value = value.strip()

        return [name.strip(), value.strip()]
