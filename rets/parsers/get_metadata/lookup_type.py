import xmltodict
from rets.models import LookupTypeModel
from rets.parsers.base import Base


class LookupTypeParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)

        base = xml.get('RETS', {}).get('METADATA-LOOKUP_TYPE', {})
        attributes = self.get_attributes(base)

        parsed = {}

        if 'DATA' in base:
            for lookup in base['DATA']:
                lookup_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=lookup)
                key = lookup_dict['MetadataEntryID']
                parsed[key] = LookupTypeModel(elements=lookup_dict, attributes=attributes)

        return parsed
