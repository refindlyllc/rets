import xmltodict
from rets.models import ObjectMetadataModel
from rets.parsers.base import Base


class ObjectParser(Base):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        if 'METADATA' in xml:
            for k, v in xml['METADATA']['METADATA-OBJECT']['Object'].items():
                object_model = ObjectMetadataModel(session=self.session,
                                                   elements=v,
                                                   attributes=xml['METADATA']['METADATA-OBJECT'])
                parsed[k] = object_model
                # not sure about this
                # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetMetadata/Resource.php#L19

        return parsed
