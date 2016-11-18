from rets.parsers.get_metadata.base import Base
from rets.models.metadata.resource_class import ResourceClass as RcModel
import xmltodict


class ResourceClass(Base):

    def parse(self, rets_session, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-CLASS', {})

        if 'Class' in base:
            if type(base['Class']) is list:
                for r_c in base['Class']:
                    attributes = {k.lstrip('@'): v for k, v in base.items() if k[0] == '@'}
                    class_obj = RcModel(attributes['Resource'])
                    class_obj.session = rets_session
                    obj = self.load_from_xml(model_obj=class_obj,
                                             xml_elements=r_c,
                                             attributes=attributes)

                    parsed[obj.elements['ClassName']] = obj

            else:
                attributes = {k.lstrip('@'): v for k, v in base.items() if k[0] == '@'}
                class_obj = RcModel(attributes['Resource'])
                class_obj.session = rets_session
                obj = self.load_from_xml(model_obj=class_obj,
                                         xml_elements=base['Class'],
                                         attributes=attributes)

                parsed[obj.elements['ClassName']] = obj

        return parsed
