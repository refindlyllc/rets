from rets.models import Results
import xmltodict
from rets.parsers.base import Base
import logging


logger = logging.getLogger('rets')


class OneXSearchCursor(Base):

    xml = None
    base = None

    def get_total_count(self):
        """
        Get the total number of records in the RETS database from the COUNT tag in the XML response
        :return: None if COUNT tag doesn't exist otherwise an integer if it does
        """
        if 'COUNT' in self.base:
            return int(self.base['COUNT'].get('@Records'))
        return None

    def get_found_max_rows(self):
        """
        The maximum number of records that can be returned per request
        :return int: The value of MAXROWS in the response
        """
        return 'MAXROWS' in self.base

    def get_delimiter(self):
        """
        Get the space delimiter used to separate values from each other in the response xml
        :return chr
        """
        if 'DELIMITER' in self.base:
            # delimiter found so we have at least a COLUMNS row to parse
            return chr(int(self.base['DELIMITER'].get('@value', 9)))
        else:
            # assume tab delimited since it wasn't given
            logger.debug('Assuming TAB delimiter since none specified in response')
            return chr(9)

    def get_column_names(self):
        """
        Get the column names from the response xml and split them with the delimiter
        :return list: a list of column names
        """
        # break out and track the column names in the response
        column_names = self.base.get('COLUMNS')

        # take out the first and last delimiter
        column_names = column_names.strip(self.get_delimiter())

        # parse and return the rest
        return column_names.split(self.get_delimiter())

    def parse(self, rets_response, parameters):
        """
        Parse the response xml given back from the rets feed.
        This converts the records and columns into a dictionary as well as extracts other information from the
        response such as the number of records returned and the total number of records in the database and returns
        eveything in a new Results object.
        :param rets_response: The response from the rets feed
        :param parameters: Information about how the response was gotten
        :return: Results
        """
        self.xml = xmltodict.parse(rets_response.text)
        self.analyze_reploy_code(xml_response_dict=self.xml)
        self.base = self.xml.get('RETS')

        rs = Results()
        rs.resource = parameters.get('ResourceMetadata')
        rs.resource_class = parameters.get('Class')
        rs.dmql = parameters.get('Query')
        rs.metadata = parameters.get('ResultKey')

        if parameters.get('RestrictedIndicator', None):
            rs.restricted_indicator = parameters.get('RestrictedIndicator', None)

        rs.headers = self.get_column_names()

        if 'DATA' in self.base:
            for line in self.base['DATA']:
                delim = self.get_delimiter()
                result_dict = self.data_columns_to_dict(columns_string=self.base.get('COLUMNS', ''),
                                                        dict_string=line,
                                                        delimiter=delim)
                rs.values.append(result_dict)

        if self.get_total_count() is not None:
            rs.total_results_count = self.get_total_count()
            logger.debug("%s values found" % rs.total_results_count)

        logger.debug('%s values' % rs.results_count)

        if self.get_found_max_rows():
            '''
            MAXROWS tag found.  the RETS server withheld records.
            if the server supports Offset, more requests can be sent to page through values
            until this tag isn't found anymore.
            '''
            rs.max_rows_reached = True
            logger.debug("Maximum rows returned in response")

        return rs
