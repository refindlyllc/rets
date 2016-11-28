import xmltodict
from rets.models import ResourceClassModel
from rets.parsers.base import Base


class ResourceClassParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-CLASS', {})

        if 'Class' in base:
            if type(base['Class']) is list:
                for r_c in base['Class']:
                    attributes = self.get_attributes(base)
                    class_obj = ResourceClassModel(resource=attributes['Resource'],
                                                   session=self.session,
                                                   elements=r_c,
                                                   attributes=attributes)

                    parsed[class_obj.elements['ClassName']] = class_obj

            else:
                attributes = self.get_attributes(base)
                class_obj = ResourceClassModel(resource=attributes['Resource'],
                                               session=self.session,
                                               elements=base['Class'],
                                               attributes=attributes)

                parsed[class_obj.elements['ClassName']] = class_obj

        return parsed
