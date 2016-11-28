

class Results(object):

    resource = None
    resource_class = None
    metadata = None
    returned_results_count = 0
    total_results_count = 0
    error = None
    results = []
    results_count = len(results)
    headers = {}
    restricted_indicator = '****'
    max_rows_reached = False

    def __repr__(self):
        return '<Results: {} Found>'.format(self.total_results_count)

    def add_record(self, record):
        record.parent = self
        self.results.append(record)

    def lists(self, field):
        l = []
        for r in self.results:
            v = r.get(field)
            if v and not r.is_restricted(field=field):
                l.append(v)
        return l
