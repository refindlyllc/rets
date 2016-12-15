try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
from rets.parsers.base import Base
from rets.exceptions import RETSException
import logging

logger = logging.getLogger('rets')


class OneXSearchCursor(Base):

    def __init__(self):
        self.parsed_rows = 0

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
                self.parsed_rows += 1  # Rows parsed with all requests
                yield data_dict

            # Handle reply code
            elif "RETS" == elem.tag:
                reply_code = elem.get('ReplyCode')
                reply_text = elem.get('ReplyText')
                if reply_code != '0':
                    msg = "RETS Error {0!s}: {1!s}".format(reply_code, reply_text)
                    raise RETSException(msg)

            # Analyze delimiter
            elif "DELIMITER" == elem.tag:
                val = elem.get("value")
                delim = chr(int(val))

            # Analyze columns
            elif "COLUMNS" == elem.tag:
                columns = elem.text.strip().split(delim)

            # handle max rows
            elif "MAXROWS" == elem.tag:
                logger.debug("MAXROWS Tag reached in XML")
                logger.debug("Received {0!s} results from this search".format(self.parsed_rows))

            else:
                # This is a tag we don't process (like COUNT)
                continue

            elem.clear()
