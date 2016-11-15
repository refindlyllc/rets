from rets.parsers.get_metadata.base import Base
from rets.models.metadata.table import Table as TbModel


class Table(Base):

    def parse(self, rets_session, response, keyed_by):

        xml = response.xml
        parsed = {}

        if 'METADATA' in xml:
            for k, v in xml['METADATA']['METADATA-TABLE'].items():
                table_obj = TbModel()
                table_obj.session = rets_session

        # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/Table.php#L19
        # https://github.com/troydavisson/PHRETS/blob/master/src/Models/Metadata/Base.php#L34
        # Don't have the magic call method. THink of a new way to do this

        return parsed
