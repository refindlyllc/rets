import xmltodict
from rets.models import ResourceClassModel
from rets.parsers.base import Base


class ResourceClassParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA-CLASS', {})
        attributes = self.get_attributes(base)

        if 'DATA' in base:
            for resource_class in base['DATA']:
                resource_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=resource_class)
                key = resource_dict['ClassName']
                parsed[key] = ResourceClassModel(elements=resource_dict, attributes=attributes)

        return parsed
