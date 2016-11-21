import xmltodict

from rets.models.metadata.lookup_type import LookupType as LtModel
from rets.parsers.get_metadata.metadata_base import MetadataBase


class LookupType(MetadataBase):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = []

        metadata_attributes = xml.get('METADATA', {}).get('METADATA-LOOKUP_TYPE', {})
        lookup_name = metadata_attributes.get('LookupType', 'Lookup')
        base = xml['METADATA']['METADATA-LOOKUP_TYPE'][lookup_name]

        for k, v in base.items():
            lookup_obj = LtModel(session=self.session)
            parsed.append(self.load_from_xml(model_obj=lookup_obj, xml_elements=v, attributes=metadata_attributes))

        return parsed
