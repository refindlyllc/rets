

class Results(object):

    def __repr__(self):
        return '<Results: {} Found in {}:{} for {}>'.format(self.total_results_count,
                                                            self.resource.StandardName,
                                                            self.resource_class,
                                                            self.dmql)

    def __len__(self):
        return len(self.results)

    def __init__(self):
        self.metadata = None
        self.resource = None
        self.resource_class = None
        self.returned_results_count = 0
        self.total_results_count = 0
        self.results_count = 0
        self.results = []
        self.headers = {}
        self.restricted_indicator = '****'
        self.max_rows_reached = False
        self.dmql = None

    def add_record(self, record):
        record.parent = self
        self.results_count += 1
        self.results.append(record)

    def lists(self, field):
        l = []
        for r in self.results:
            v = r.get(field)
            if v and not r.is_restricted(field=field):
                l.append(v)
        return l
