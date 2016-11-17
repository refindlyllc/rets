from rets.parsers.get_metadata.base import Base
from rets.models.metadata.resource import Resource as ReModel
import xmltodict


class Resource(Base):

    def parse(self, rets_session, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        if 'METADATA' in xml:

            for k, v in xml['METADATA']['METADATA-RESOURCE']['Resource']:
                resource_obj = ReModel()
                resource_obj.session = rets_session
                obj = self.load_from_xml(model_obj=resource_obj,
                                         xml_elements=v,
                                         attributes=xml['METADATA']['METADATA-RESOURCE'])

                parsed[k] = obj
                # Not sure about this
                # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/Resource.php#L19

        return parsed
