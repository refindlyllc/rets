import xmltodict
from rets.models import ResourceModel
from rets.parsers.base import Base


class ResourceParser(Base):
    metadata_type = 'METADATA-RESOURCE'

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA-RESOURCE', {})
        attributes = self.get_attributes(base)

        parsed = {}
        if 'DATA' in base:
            for resource in base['DATA']:
                resource_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=resource)
                key = resource_dict['ResourceID']
                parsed[key] = ResourceModel(elements=resource_dict, attributes=attributes)

        return parsed
