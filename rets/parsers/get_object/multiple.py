from .single import SingleObjectParser
import re
from rets.parsers.base import Base


class MultipleObjectParser(Base):

    @staticmethod
    def parse(response):
        """
        Parse multiple objects from the RETS feed
        :param response: The response from the feed
        :return: list of SingleObjectParser
        """

        parsed = []

        if response.text is None:
            return parsed

        #  help bad responses be more multipart compliant
        body = '\r\n' + response.text + '\r\n'

        # multipart
        match = re.match(pattern='/boundary\=\"(.*?)\"/', string=response.headers.get('Content-Type'))
        if not match:
            match = re.match(pattern='/boundary\=(.*?)(\s|$|\;)/', string=response.headers.get('Content-Type'))

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