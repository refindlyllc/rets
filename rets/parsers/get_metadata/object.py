import xmltodict
from rets.models import ObjectMetadataModel
from rets.parsers.base import Base


class ObjectParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-OBJECT', {})
        attributes = self.get_attributes(base)
        parsed = {}

        if 'Object' in base:
            for o in base['Object']:
                object_model = ObjectMetadataModel(elements=o, attributes=attributes)
                parsed[o['VisibleName']] = object_model


                # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/Resource.php#L19

        return parsed
