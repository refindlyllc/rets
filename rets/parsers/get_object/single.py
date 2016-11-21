from rets.models.object import Object
from rets.exceptions import RETSException
from rets.parsers.base import Base
import xmltodict


class Single(Base):

    def parse(self, response):

        if response.status_code != 200:
            raise RETSException("")

        headers = response.headers

        obj = Object()
        obj.content = response.text
        obj.content_description = headers.get('Content-Description')
        obj.content_sub_description = headers.get('Content-Sub-Description')
        obj.content_id = headers.get('Content-ID')
        obj.object_id = headers.get('Object-ID')
        obj.content_type = headers.get('Content-Type')
        obj.location = headers.get('Location')
        obj.mime_version = headers.get('MIME-Version')
        obj.preferred = headers.get('Preferred')

        return obj