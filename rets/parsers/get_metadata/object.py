from rets.parsers.get_metadata.base import Base
from rets.models.metadata.object import Object as ObModel
import xmltodict


class Object(Base):

    def parse(self, rets_session, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        if 'METADATA' in xml:
            for k, v in xml['METADATA']['METADATA-OBJECT']['Object'].items():
                object_model = ObModel()
                object_model.session = rets_session
                obj = self.load_from_xml(model_obj=object_model,
                                         xml_elements=v,
                                         attributes=xml['METADATA']['METADATA-OBJECT'])

                parsed[k] = obj
                # not sure about this
                # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/Resource.php#L19

        return parsed
