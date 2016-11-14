

class Results(object):

    resource = None
    result_class = None
    session = None
    metadata = None
    total_results_count = 0
    error = None
    results = {}
    headers = {}
    restricted_indicator = '****'
    max_rows_reached = False

    def add_record(self, record):
        record.parent = self
        self.results.append(record)

    @property
    def results_count(self):
        return len(self.results)
