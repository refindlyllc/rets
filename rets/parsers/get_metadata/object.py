import xmltodict
from rets.models import ObjectMetadataModel
from rets.parsers.base import Base


class ObjectParser(Base):
    metadata_type = 'METADATA-OBJECT'

    def parse(self, response):
        """
        Parse an object from the rets feed
        :param response: the response from the server
        :return: dict
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA-OBJECT', {})
        attributes = self.get_attributes(base)

        parsed = {}
        if 'DATA' in base:
            for o in base['DATA']:
                object_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=o)
                key = object_dict['VisibleName']
                parsed[key] = ObjectMetadataModel(elements=object_dict, attributes=attributes)

        return parsed
