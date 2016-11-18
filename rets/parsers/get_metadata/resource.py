from rets.parsers.get_metadata.base import Base
from rets.models.metadata.resource import Resource as ReModel
import xmltodict


class Resource(Base):

    def parse(self, rets_session, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-RESOURCE', {})

        if 'Resource' in base:
            for resource in base['Resource']:
                resource_obj = ReModel()
                resource_obj.session = rets_session
                obj = self.load_from_xml(model_obj=resource_obj,
                                         xml_elements=resource,
                                         attributes={k.lstrip('@'): v for k, v in base.items() if k[0] == '@'})

                parsed[obj.elements['ResourceID']] = obj

        return parsed
