from rets.models.object import Object
from rets.parsers.base import Base


class SingleObjectParser(Base):

    def parse(self, response):

        obj = Object()
        obj.content = response.content
        obj.content_description = response.headers.get('Content-Description')
        obj.content_sub_description = response.headers.get('Content-Sub-Description')
        obj.content_id = response.headers.get('Content-ID')
        obj.object_id = response.headers.get('Object-ID')
        obj.content_type = response.headers.get('Content-Type')
        obj.location = response.headers.get('Location')
        obj.mime_version = response.headers.get('MIME-Version')
        obj.preferred = response.headers.get('Preferred')

        return obj
