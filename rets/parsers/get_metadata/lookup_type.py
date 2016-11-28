import xmltodict
from rets.models import LookupTypeModel
from rets.parsers.base import Base


class LookupTypeParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = []

        metadata_attributes = xml.get('METADATA', {}).get('METADATA-LOOKUP_TYPE', {})
        lookup_name = metadata_attributes.get('LookupType', 'Lookup')
        base = xml['METADATA']['METADATA-LOOKUP_TYPE'][lookup_name]

        for k, v in base.items():
            lookup_obj = LookupTypeModel(session=self.session, elements=v, attributes=metadata_attributes)
            parsed.append(lookup_obj)

        return parsed
