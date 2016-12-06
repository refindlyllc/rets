import xmltodict
from rets.models import TableModel
from rets.parsers.base import Base


class TableParser(Base):
    metadata_type = 'METADATA-TABLE'

    def parse(self, response):
        """
        Parse the table in a Class
        :param response: The xml response
        :return: dict
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA-TABLE', {})
        attributes = self.get_attributes(base)

        parsed = {}
        if 'DATA' in base:
            for field in base['DATA']:
                field_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=field)
                key = field_dict['SystemName']
                parsed[key] = TableModel(elements=field_dict, attributes=attributes)

        return parsed
