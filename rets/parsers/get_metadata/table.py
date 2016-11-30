import xmltodict
from rets.models import TableModel
from rets.parsers.base import Base


class TableParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-TABLE', {})

        attributes = self.get_attributes(input_dict=base)
        for field in base['Field']:

            table_obj = TableModel(elements=field, attributes=attributes)
            parsed[table_obj.SystemName] = table_obj

        return parsed
