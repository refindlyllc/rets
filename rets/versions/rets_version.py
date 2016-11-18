from rets.exceptions import InvalidRETSVersion
from distutils.version import StrictVersion


class RETSVersion(object):
    VERSION_1_5 = '1.5'
    VERSION_1_7 = '1.7'
    VERSION_1_7_1 = '1.7.1'
    VERSION_1_7_2 = '1.7.2'
    VERSION_1_8 = '1.8'

    number = None

    valid_versions = [
        VERSION_1_5,
        VERSION_1_7,
        VERSION_1_7_1,
        VERSION_1_7_2,
        VERSION_1_8,
    ]

    def __init__(self, version):
        self.set_versions(version=version)

    def __str__(self):
        return str(self.number)

    def set_versions(self, version):
        self.number = version.lstrip('RETS/')

        if self.number not in self.valid_versions:
            raise InvalidRETSVersion("RETS version {} given is not understood".format(self.number))

        return self

    def as_header(self):
        return 'RETS/{}'.format(self.number)

    def is_1_5(self):
        return self.number == self.VERSION_1_5

    def is_1_7(self):
        return self.number == self.VERSION_1_7

    def is_1_7_2(self):
        return self.number == self.VERSION_1_7_2

    def is_1_8(self):
        return self.number == self.VERSION_1_8

    def is_at_least(self, version):
        return StrictVersion(self.number) >= StrictVersion(version)

    def at_least_1_5(self):
        return self.is_at_least(self.VERSION_1_5)

    def at_least_1_7(self):
        return self.is_at_least(self.VERSION_1_7)

    def at_least_1_7_2(self):
        return self.is_at_least(self.VERSION_1_7_2)

    def at_least_1_8(self):
        return self.is_at_least(self.VERSION_1_8)