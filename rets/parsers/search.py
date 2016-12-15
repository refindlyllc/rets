try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
from rets.parsers.base import Base
from rets.exceptions import RETSException


class OneXSearchCursor(Base):

    def __init__(self):
        self.parsed_rows = 0
        self.requests_rows = 0

    def generator(self, response):
        """
        Takes a response socket connection and iteratively parses and yields the results as python dictionaries.
        :param response: a Requests response object with stream=True
        :return:
        """

        delim = '\t'  # Default to tab delimited
        columns = []

        events = ET.iterparse(response.raw)
        for event, elem in events:
            # Analyze search record data
            if "DATA" == elem.tag:
                data_dict = {column: data for column, data in zip(columns, elem.text.strip().split(delim))}
                self.requests_rows += 1  # Rows parsed with this requests
                self.parsed_rows += 1  # Rows parsed with all requests
                yield data_dict

            # Handle reply code
            elif "RETS" == elem.tag:
                reply_code = elem.get('ReplyCode')
                reply_text = elem.get('ReplyText')
                if reply_code != '0':
                    msg = "RETS Error {0!s}: {1!s}".format(reply_code, reply_text)
                    raise RETSException(msg)

                # When recursive requests, reset this value to 0. This is used by MAXROWS below.
                self.requests_rows = 0

            # Analyze delimiter
            elif "DELIMITER" == elem.tag:
                val = elem.get("value")
                delim = chr(int(val))

            # Analyze columns
            elif "COLUMNS" == elem.tag:
                columns = elem.text.strip().split(delim)

            # handle max rows
            elif "MAXROWS" == elem.tag:
                if self.requests_rows > 0:
                    # Reached the end of the XML, there may be more results on the next offset.
                    continue

            else:
                # This is a tag we don't process (like COUNT)
                continue

            elem.clear()
