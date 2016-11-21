

class Results(object):

    resource = None
    result_class = None
    metadata = None
    returned_results_count = 0
    total_results_count = 0
    error = None
    results = []
    results_count = len(results)
    headers = {}
    restricted_indicator = '****'
    max_rows_reached = False

    def add_record(self, record):
        record.parent = self
        self.results.append(record)
