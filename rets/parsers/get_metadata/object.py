import xmltodict
from rets.models import ObjectMetadataModel
from rets.parsers.base import Base


class ObjectParser(Base):
    metadata_type = 'METADATA-OBJECT'

    def parse(self, response):
        """
        Parse an object from the rets feed
        :param response: the response from the server
        :return: dict
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-OBJECT', {})
        attributes = self.get_attributes(base)

        parsed = {}
        if 'Object' in base:
            for o in base['Object']:
                object_model = ObjectMetadataModel(elements=o, attributes=attributes)
                parsed[o['VisibleName']] = object_model


                # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/Resource.php#L19

        return parsed
