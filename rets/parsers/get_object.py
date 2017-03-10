import xmltodict
from rets.exceptions import ParseError
from rets.parsers.base import Base
import sys
import hashlib

PY2 = sys.version_info[0] == 2


class MultipleObjectParser(Base):
    """Parses multiple object responses such as multiple images in a multi-part response"""

    def parse(self, response):
        """
        Parse multiple objects from the RETS feed. A lot of string methods are used to handle the response before
        encoding it back into bytes for the object.
        :param response: The response from the feed
        :return: list of SingleObjectParser
        """
        if 'xml' in response.headers.get('Content-Type'):
            # Got an XML response, likely an error code.
            xml = xmltodict.parse(response.text)
            self.analyze_reploy_code(xml_response_dict=xml)

        parsed = []

        # multipart
        '''
        From this
        'multipart/parallel; boundary="874e43d27ec6d83f30f37841bdaf90c7"; charset=utf-8'
        get this
        874e43d27ec6d83f30f37841bdaf90c7
        '''
        boundary = None
        for part in response.headers.get('Content-Type', '').split(';'):
            if 'boundary=' in part:
                boundary = part.split('=', 1)[1].strip('\"')

        if not boundary:
            raise ParseError("Was not able to find the boundary between objects in a multipart response")

        if response.content is None:
            return parsed

        response_string = response.content if PY2 else response.content.decode(response.encoding, 'replace')

        #  help bad responses be more multipart compliant
        whole_body = '\r\n{0!s}\r\n'.format(response_string).strip('\r\n')

        # The boundary comes with some characters
        boundary = '\r\n--{0!s}\r\n'.format(boundary)

        # Split on the boundary
        multi_parts = whole_body.strip(boundary).split(boundary)

        # go through each part of the multipart message
        for part in multi_parts:
            header, body = part.split('\r\n\r\n', 1)
            part_header_dict = {k.strip(): v.strip() for k, v in (h.split(':') for h in header.split('\r\n'))}
            obj = dict()
            obj['content'] = body if PY2 else body.encode(response.encoding)

            md = hashlib.md5()
            md.update(obj['content'])
            obj['content_md5'] = md.hexdigest()

            obj['content_description'] = part_header_dict.get('Content-Description',
                                                              response.headers.get('Content-Description'))
            obj['content_sub_description'] = part_header_dict.get('Content-Sub-Description',
                                                                  response.headers.get('Content-Sub-Description'))
            obj['content_id'] = part_header_dict.get('Content-ID',
                                                     response.headers.get('Content-ID'))
            obj['object_id'] = part_header_dict.get('Object-ID',
                                                    response.headers.get('Object-ID'))
            obj['content_type'] = part_header_dict.get('Content-Type',
                                                       response.headers.get('Content-Type'))
            obj['location'] = part_header_dict.get('Location',
                                                   response.headers.get('Location'))
            obj['mime_version'] = part_header_dict.get('MIME-Version',
                                                       response.headers.get('MIME-Version'))
            obj['preferred'] = part_header_dict.get('Preferred',
                                                    response.headers.get('Preferred'))


            parsed.append(obj)

        return parsed


class SingleObjectParser(Base):

    def parse(self, response):
        """
        Parse a single object from the RETS feed
        :param response: The response from the RETS server
        :return: Object
        """
        if 'xml' in response.headers.get('Content-Type'):
            # Got an XML response, likely an error code.
            xml = xmltodict.parse(response.text)
            self.analyze_reploy_code(xml_response_dict=xml)

        obj = dict()
        obj['content'] = response.content

        md = hashlib.md5()
        md.update(obj['content'])
        obj['content_md5'] = md.hexdigest()

        obj['content_description'] = response.headers.get('Content-Description')
        obj['content_sub_description'] = response.headers.get('Content-Sub-Description')
        obj['content_id'] = response.headers.get('Content-ID')
        obj['object_id'] = response.headers.get('Object-ID')
        obj['content_type'] = response.headers.get('Content-Type')
        obj['location'] = response.headers.get('Location')
        obj['mime_version'] = response.headers.get('MIME-Version')
        obj['preferred'] = response.headers.get('Preferred')

        return obj
