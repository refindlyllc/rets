from rets.session import Session
from rets.models.search.record import Record
from rets.models.search.results import Results
import re


class OneX(object):
    def parse(self, rets_session, response, parameters):
        xml = response.xml

        rs = Results()
        rs.session = rets_session
        rs.resource = parameters.get('SearchType')
        rs.result_class = parameters.get('Class')

        if parameters.get('RestrictedIndicator', None):
            rs.restricted_indicator = parameters.get('RestrictedIndicator', None)

        rs.headers = self.get_column_names(rets_session, xml, parameters)
        print("%s column headers/fields given" % len(rs.headers))

        self.parse_records(rets_session, xml, parameters, rs)

        if self.get_total_count(rets_session, xml, parameters) is not None:
            rs.total_results_count = self.get_total_count(rets_session, xml, parameters)
            print("%s results found" % rs.total_results_count)

        print('%s results' % rs.results_count)

        if self.found_max_rows(rets_session, xml, parameters):
            '''
            MAXROWS tag found.  the RETS server withheld records.
            if the server supports Offset, more requests can be sent to page through results
            until this tag isn't found anymore.
            '''
            rs.max_rows_reached = True
            print("Maximum rows returned in response")

        return rs

    @staticmethod
    def get_delimiter(rets_session, xml, parameters):
        if 'DELIMITER' in xml:
            # delimiter found so we have at least a COLUMNS row to parse
            return chr(xml['DELIMITER'].get('attributes', {}).get('values'))
        else:
            # assume tab delimited since it wasn't given
            print('Assuming TAB delimiter since none specified in response')
            return chr(9)

    def get_column_names(self, rets_session, xml, parameters):
        delim = self.get_delimiter(rets_session, xml, parameters)

        # break out and track the column names in the response
        column_names = xml.get('COLUMNS', [None]).pop(0)

        # take out the first delimiter
        column_names = re.sub(pattern="/^{$delim}/", repl="", string=column_names)

        # take out the last delimiter
        column_names = re.sub(pattern="/{$delim}\$/", repl="", string=column_names)

        # parse and return the reest
        return column_names.split(delim)

    def parse_records(self, rets_session, xml, parameters, rs):
        if 'DATA' in xml:
            for line in xml['DATA']:
                rs.add_record(self.parse_record_from_line(rets_session, xml, parameters, line, rs))


    def parse_record_from_line(self, rets_session, xml, parameters, line, rs):
        delim = self.get_delimiter(rets_session, xml, parameters)

        r = Record()
        field_data = str(line)

        # split up DATA row on delimiter found earlier
        field_data = re.sub(pattern="/^{$delim}/", repl="", string=field_data)
        field_data = re.sub(pattern="/{$delim}\$/", repl="", string=field_data)
        field_data = field_data.split(delim)

        for key, name in rs.headers:
            # assign each value to its name retrieve in the COLUMNS earlier
            r.values[name] = field_data[key]

        return r

    def get_total_count(self, rets_session, xml, parameters):
        if 'COUNT' in xml:
            return int(xml['COUNT'].get('attributes', {}).get('Records'))
        return None

    def found_max_rows(self, rets_session, xml, parameters):
        if 'MAXROWS' in xml:
            return True
        return False
