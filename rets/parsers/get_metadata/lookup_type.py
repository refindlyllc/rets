import xmltodict
from rets.models import LookupTypeModel
from rets.parsers.base import Base


class LookupTypeParser(Base):
    metadata_type = 'METADATA-LOOKUP_TYPE'

    def parse(self, response):
        """
        Parse the lookup types in a rets feed
        :param response: The response from a rets feed
        :return: dict
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA-LOOKUP_TYPE', {})
        attributes = self.get_attributes(base)

        parsed = {}
        if 'DATA' in base:
            for lookup in base['DATA']:
                lookup_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=lookup)
                key = lookup_dict['MetadataEntryID']
                parsed[key] = LookupTypeModel(elements=lookup_dict, attributes=attributes)

        return parsed
