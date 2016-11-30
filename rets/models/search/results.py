

class Results(object):

    def __repr__(self):
        return '<Results: {} Found>'.format(self.total_results_count)

    def __len__(self):
        return len(self.results)

    def __init__(self):
        self.resource = None
        self.resource_class = None
        self.metadata = None
        self.returned_results_count = 0
        self.total_results_count = 0
        self.error = None
        self.results = []
        self.results_count = len(self.results)
        self.headers = {}
        self.restricted_indicator = '****'
        self.max_rows_reached = False

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
