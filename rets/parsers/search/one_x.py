import logging
import xmltodict
from rets.models import ResultsSet
from rets.parsers.base import Base

logger = logging.getLogger('rets')


class OneXSearchCursor(Base):

    def parse(self, rets_response, parameters, results_set=None):
        """
        Parse the response xml given back from the rets feed.
        This converts the records and columns into a dictionary as well as extracts other information from the
        response such as the number of records returned and the total number of records in the database and returns
        eveything in a new Results object.
        :param rets_response: The response from the rets feed
        :param parameters: Information about how the response was gotten
        :param results_set: a ResultsSet object. This is passed when additional response data needs to be added to an
        existing result set
        :return: Results
        """
        xml = xmltodict.parse(rets_response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS')

        if 'DELIMITER' in base:
            # delimiter found so we have at least a COLUMNS row to parse
            delim = chr(int(base['DELIMITER'].get('@value', 9)))
        else:
            # assume tab delimited since it wasn't given
            logger.debug('Assuming TAB delimiter since none specified in response')
            delim = chr(9)

        if results_set:
            rs = results_set
        else:
            rs = ResultsSet()
            rs.resource = parameters.get('SearchType')
            rs.resource_class = parameters.get('Class')
            rs.dmql = parameters.get('Query')
            rs.metadata = parameters.get('ResultKey')
            if parameters.get('RestrictedIndicator'):
                rs.restricted_indicator = parameters['RestrictedIndicator']

            rs.headers = base.get('COLUMNS', '').strip(delim).split(delim)

            if 'COUNT' in base:
                rs.total_results_count = int(base['COUNT'].get('@Records'))
                logger.debug("%s values found" % rs.total_results_count)
            else:
                rs.total_results_count = None

        if 'DATA' in base:
            for line in base['DATA']:
                result_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''),
                                                        dict_string=line,
                                                        delimiter=delim)
                rs.values.append(result_dict)

        logger.debug('%s results' % rs.results_count)

        if rs.total_results_count == rs.results_count or rs.total_results_count is None:
            '''
            MAXROWS tag found.  the RETS server withheld records.
            if the server supports Offset, more requests can be sent to page through values
            until this tag isn't found anymore.
            '''
            rs.max_rows_reached = True
            logger.debug("Maximum rows returned in response")

        return rs
