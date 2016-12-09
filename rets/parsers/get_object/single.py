from rets.parsers.base import Base
import xmltodict


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
        obj['content_description'] = response.headers.get('Content-Description')
        obj['content_sub_description'] = response.headers.get('Content-Sub-Description')
        obj['content_id'] = response.headers.get('Content-ID')
        obj['object_id'] = response.headers.get('Object-ID')
        obj['content_type'] = response.headers.get('Content-Type')
        obj['location'] = response.headers.get('Location')
        obj['mime_version'] = response.headers.get('MIME-Version')
        obj['preferred'] = response.headers.get('Preferred')

        return obj
