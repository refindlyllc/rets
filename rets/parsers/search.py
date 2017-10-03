import logging
from xml.etree import ElementTree as ET

from six import BytesIO

from rets.exceptions import RETSException, MaxrowException
from rets.parsers.base import Base

logger = logging.getLogger('rets')


class OneXSearchCursor(Base):
    """Parses Search Result Data"""

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
        response.raw.decode_content = True
        events = ET.iterparse(BytesIO(response.content))

        results = []
        for event, elem in events:
            # Analyze search record data
            if "DATA" == elem.tag:
                data_dict = {column: data for column, data in zip(columns, elem.text.split(delim)) if column != ''}
                self.parsed_rows += 1  # Rows parsed with all requests
                results.append(data_dict)

            # Handle reply code
            elif "RETS" == elem.tag:
                reply_code = elem.get('ReplyCode')
                reply_text = elem.get('ReplyText')

                if reply_code == '20201':
                    # RETS Response 20201 - No Records Found
                    # Generator should continue and return nothing
                    continue
                elif reply_code != '0':
                    msg = "RETS Error {0!s}: {1!s}".format(reply_code, reply_text)
                    raise RETSException(msg)

            # Analyze delimiter
            elif "DELIMITER" == elem.tag:
                val = elem.get("value")
                delim = chr(int(val))

            # Analyze columns
            elif "COLUMNS" == elem.tag:
                columns = elem.text.split(delim)

            # handle max rows
            elif "MAXROWS" == elem.tag:
                logger.debug("MAXROWS Tag reached in XML")
                logger.debug("Received {0!s} results from this search".format(self.parsed_rows))
                raise MaxrowException(results)

            else:
                # This is a tag we don't process (like COUNT)
                continue

            elem.clear()

        return results
