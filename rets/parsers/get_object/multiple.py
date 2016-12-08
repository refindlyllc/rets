from .single import SingleObjectParser
from rets.exceptions import ParseError
import xmltodict
from rets.parsers.base import Base


class MultipleObjectParser(Base):

    def parse(self, response):
        """
        Parse multiple objects from the RETS feed
        :param response: The response from the feed
        :return: list of SingleObjectParser
        """
        if 'xml' in response.headers.content_type:
            # Got an XML response, likely an error code.
            xml = xmltodict.parse(response.text)
            self.analyze_reploy_code(xml_response_dict=xml)

        parsed = []

        if response.content is None:
            return parsed

        #  help bad responses be more multipart compliant
        body = '\r\n{0!s}\r\n'.format(response.text.strip('\r\n'))

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
                break
        if not boundary:
            raise ParseError("Was not able to find the boundary between objects in a multipart response")

        # The boundary comes with some characters
        boundary = '\r\n--{0!s}\r\n'.format(boundary)

        # Split on the boundary
        multi_parts = body.split(boundary)

        # go through each part of the multipart message
        for part in multi_parts:
            # Not sure what guzzle is doing
            # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetObject/Multiple.php#L51
            parser = SingleObjectParser()
            obj.parse(part)
            parsed.append(obj)

        return parsed
        '''
        match = re.match(pattern='/boundary\=\"(.*?)\"/', string=response.headers.get('Content-Type'))
        if not match:
            match = re.match(pattern='/boundary\=(.*?)(\s|$|\;)/', string=response.headers.get('Content-Type'))
        'multipart/parallel; boundary="874e43d27ec6d83f30f37841bdaf90cf"; charset=utf-8'
        boundary = match.group(1)

        # strip quotes off of boundary
        boundary = re.sub(pattern='/^\"(.*?)\"$/', repl='\1', string=boundary)

        # clean up the body to remove a reamble and epilogue
        body = re.sub(pattern='/^(.*?)\r\n--' + boundary + '\r\n/', repl="\r\n--" + boundary + "\r\n", string=body)

        # make the last one look like the rest for easier parsing
        body = re.sub(pattern='/\r\n--' + boundary + '--/', repl="\r\n--" + boundary + "\r\n", string=body)

        # cut off the message
        multi_parts = body.split("\r\n--" + boundary + "\r\n")

        # take off anything that happens before the first boundary (the preamble)
        multi_parts.pop(0)

        # take off anything after the last boundary (the epilogue)
        multi_parts.pop(-1)

        # go through each part of the multipart message
        for part in multi_parts:
            # Not sure what guzzle is doing
            # https://github.com/troydavisson/PHRETS/blob/master/src/Parsers/GetObject/Multiple.php#L51
            obj = SingleObjectParser()
            obj.parse(part)
            parsed.append(obj)

        return parsed
        '''