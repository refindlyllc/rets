from rets.parsers.get_metadata.base import Base
from rets.models.metadata.resource_class import ResourceClass as RcModel


class ResourceClass(Base):

    def parse(self, rets_session, response):

        xml = response.xml
        parsed = {}

        if 'METADATA' in xml:
            for k, v in xml['METADATA']['METADATA-CLASS']['Class']:
                class_obj = RcModel()
                class_obj.session = rets_session
                obj = self.load_from_xml(model_obj=class_obj,
                                         xml_elements=v,
                                         attributes=xml['METADATA']['METADATA-CLASS'])
                parsed[k] = obj  # not sure about this line
                # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/ResourceClass.php#L19

        return parsed
