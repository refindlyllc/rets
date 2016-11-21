import xmltodict

from rets.models.metadata.resource_class import ResourceClass as RcModel
from rets.parsers.get_metadata.metadata_base import MetadataBase

class ResourceClass(MetadataBase):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-CLASS', {})

        if 'Class' in base:
            if type(base['Class']) is list:
                for r_c in base['Class']:
                    attributes = self.get_attributes(base)
                    class_obj = RcModel(resource=attributes['Resource'], session=self.session)
                    obj = self.load_from_xml(model_obj=class_obj,
                                             xml_elements=r_c,
                                             attributes=attributes)

                    parsed[obj.elements['ClassName']] = obj

            else:
                attributes = self.get_attributes(base)
                class_obj = RcModel(resource=attributes['Resource'], session=self.session)
                obj = self.load_from_xml(model_obj=class_obj,
                                         xml_elements=base['Class'],
                                         attributes=attributes)

                parsed[obj.elements['ClassName']] = obj

        return parsed
