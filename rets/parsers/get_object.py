import xmltodict
from rets.exceptions import ParseError
from rets.parsers.base import Base
import sys
import hashlib

PY2 = sys.version_info[0] == 2


class ObjectParser(Base):

    @staticmethod
    def _response_object_from_header(obj_head_dict, content=None):
        obj = dict()
        obj['content_description'] = obj_head_dict.get('Content-Description')
        obj['content_sub_description'] = obj_head_dict.get('Content-Sub-Description')
        obj['content_id'] = obj_head_dict.get('Content-ID')
        obj['object_id'] = obj_head_dict.get('Object-ID')
        obj['content_type'] = obj_head_dict.get('Content-Type')
        obj['location'] = obj_head_dict.get('Location')
        obj['mime_version'] = obj_head_dict.get('MIME-Version')
        obj['preferred'] = obj_head_dict.get('Preferred')

        if content:
            md = hashlib.md5()
            md.update(content)
            obj['content'] = content
            obj['content_md5'] = md.hexdigest()
        else:
            obj['content'] = content
            obj['content_md5'] = None
        return obj


class MultipleObjectParser(ObjectParser):
    """Parses multiple object responses such as multiple images in a multi-part response"""

    def _get_multiparts(self, response):
        # multipart
        '''
        From this
        'multipart/parallel; boundary="874e43d27ec6d83f30f37841bdaf90c7"; charset=utf-8'
        get this
        --874e43d27ec6d83f30f37841bdaf90c7
        '''
        boundary = None
        for part in response.headers.get('Content-Type', '').split(';'):
            if 'boundary=' in part:
                boundary = '--{}'.format(part.split('=', 1)[1].strip('\"'))

        if not boundary:
            raise ParseError("Was not able to find the boundary between objects in a multipart response")

        if response.content is None:
            return []

        response_string = response.content if PY2 else response.content.decode(response.encoding, 'replace')

        #  help bad responses be more multipart compliant
        whole_body = response_string.strip('\r\n')
        no_front_boundary = whole_body.strip(boundary)
        # The boundary comes with some characters

        multi_parts = []
        for part in no_front_boundary.split(boundary):
            multi_parts.append(part.strip('\r\n'))

        return multi_parts

    def parse_image_response(self, response):
        """
        Parse multiple objects from the RETS feed. A lot of string methods are used to handle the response before
        encoding it back into bytes for the object.
        :param response: The response from the feed
        :return: list of SingleObjectParser
        """
        if 'xml' in response.headers.get('Content-Type'):
            # Got an XML response, likely an error code.
            xml = xmltodict.parse(response.text)
            self.analyze_reply_code(xml_response_dict=xml)

        multi_parts = self._get_multiparts(response)
        parsed = []
        # go through each part of the multipart message
        for part in multi_parts:
            clean_part = part.strip('\r\n\r\n')
            if '\r\n\r\n' in clean_part:
                header, body = clean_part.split('\r\n\r\n', 1)
            else:
                header = clean_part
                body = None
            part_header_dict = {k.strip(): v.strip() for k, v in (h.split(':', 1) for h in header.split('\r\n'))}

            # Some multipart requests respond with a text/XML part stating an error
            if 'xml' in part_header_dict.get('Content-Type'):
                # Got an XML response, likely an error code.
                xml = xmltodict.parse(body)
                self.analyze_reply_code(xml_response_dict=xml)

            if body:
                obj = self._response_object_from_header(
                    obj_head_dict=part_header_dict,
                    content=body if PY2 else body.encode(response.encoding))
            else:
                obj = self._response_object_from_header(obj_head_dict=part_header_dict)
            parsed.append(obj)
        return parsed


class SingleObjectParser(ObjectParser):

    def parse_image_response(self, response):
        """
        Parse a single object from the RETS feed
        :param response: The response from the RETS server
        :return: Object
        """
        if 'xml' in response.headers.get('Content-Type'):
            # Got an XML response, likely an error code.
            xml = xmltodict.parse(response.text)
            self.analyze_reply_code(xml_response_dict=xml)

        obj = self._response_object_from_header(
            obj_head_dict=response.headers,
            content=response.content)
        return obj
