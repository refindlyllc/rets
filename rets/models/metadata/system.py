from rets.models.metadata.base import Base


class System(Base):
    elements = [
        'SystemID',
        'SystemDescription',
        'TimeZoneOffset',
        'Comments',
        'Version',
    ]

    def get_resources(self):
        return self.get_resources()
