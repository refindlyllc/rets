import xmltodict
from rets.models import TableModel
from rets.parsers.base import Base


class TableParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        base = xml.get('RETS', {}).get('METADATA-TABLE', {})
        attributes = self.get_attributes(base)

        if 'DATA' in base:
            for field in base['DATA']:
                field_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=field)
                key = field_dict['SystemName']
                parsed[key] = TableModel(elements=field_dict, attributes=attributes)

        return parsed
