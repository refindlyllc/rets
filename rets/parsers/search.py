import logging
#from xml.etree import ElementTree as ET
from lxml import etree as ET
#from lxml.etree import XMLParser
#from lxml import etree
import xmltodict
from io import StringIO
from rets.parsers.base import Base
logger = logging.getLogger('rets')


class OneXSearchCursor(Base):

    def __init__(self):
        self.parsed_rows = 0
        self.requests_rows = 0

    def generator(self, response):
        """
        Takes a response socket connection and iteratively parses the results.
        :param xml_stream:
        :return:
        """

        delim = '\t'  # Default to tab delimited
        columns = []

        from io import StringIO
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
