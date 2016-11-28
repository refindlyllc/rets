import xmltodict
from rets.models import ResourceModel
from rets.parsers.base import Base


class ResourceParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-RESOURCE', {})

        if 'DATA' in base:
            for resource in base['DATA']:
                resource_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=resource)
                resource_obj = ResourceModel(session=self.session,
                                             elements=resource_dict,
                                             attributes=self.get_attributes(base))
                key = resource_dict['ResourceID']
                parsed[key] = resource_obj

        return parsed
