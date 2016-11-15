from rets.parsers.get_metadata.base import Base
from rets.models.metadata.lookup_type import LookupType as LtModel


class LookupType(Base):

    def parse(self, rets_session, response):

        xml = response.xml
        parsed = []

        metadata_attributes = xml.get('METADATA', {}).get('METADATA-LOOKUP_TYPE', {})
        lookup_name = metadata_attributes.get('LookupType', 'Lookup')
        base = xml['METADATA']['METADATA-LOOKUP_TYPE'][lookup_name]

        for k, v in base.items():
            lookup_obj = LtModel()
            lookup_obj.session = rets_session
            parsed.append(self.load_from_xml(model_obj=lookup_obj, xml_elements=v, attributes=metadata_attributes))

        return parsed
