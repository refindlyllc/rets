from rets.exceptions import AutomaticPaginationError
from .one_x import OneXSearchCursor
from rets.parsers.base import Base


class RecursiveOneXCursor(Base):

    def parse(self, response, parameters):
        # we're  giving the first response automatically so parse this and start the recursion

        parser = OneXSearchCursor()
        rs = parser.parse(rets_response=response, parameters=parameters)

        while rs.max_rows_reached is False:
            pms = parameters

            print("Continuing pagination...")
            print("Current count collected already: " + rs.count)

            resource = pms['SearchType']
            rs_class = pms['Class']
            query = pms.get('Query', None)
            pms['Offset'] = rs.returned_results_count + 1

            # This might cause issues
            del pms['SearchType']
            del pms['Class']
            del pms['Query']

            inner_rs = self.session.Search(resource, rs_class, pms, False)
            rs.total_records_count = inner_rs.total_records_count
            rs.max_rows_reached = inner_rs.max_rows_reached

            if self.is_pagination_broken(rs, inner_rs):
                raise (AutomaticPaginationError("Automatic pagination doesn't appear to be supported by the server"))

            for ir in inner_rs:
                rs.result.append(ir)

        return rs

    @staticmethod
    def is_pagination_broken(big, small):
        return list(big[0]) == list(small[0])