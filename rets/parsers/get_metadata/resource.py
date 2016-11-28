import xmltodict

from rets.models.metadata.resource import Resource as ReModel
from rets.parsers.get_metadata.metadata_base import MetadataBase


class Resource(MetadataBase):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-RESOURCE', {})

        if 'DATA' in base:
            for resource in base['DATA']:
                resource_obj = ReModel(session=self.session)
                obj = self.load_from_xml(model_obj=resource_obj,
                                         xml_elements=resource,
                                         attributes=self.get_attributes(base))

                parsed[obj.elements['ResourceID']] = obj

        return parsed
