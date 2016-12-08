

class ResultsSet(object):

    def __init__(self):
        self.resource = None
        self.resource_class = None
        self.total_results_count = 0
        self.values = []
        self.headers = {}
        self.restricted_indicator = '****'
        self.max_rows_reached = False
        self.dmql = None

    def __repr__(self):
        return '<ResultsSet: {} Found in {}:{} for {}>'.format(self.results_count,
                                                               self.resource,
                                                               self.resource_class,
                                                               self.dmql)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        for i in self.values:
            yield i

    @property
    def results_count(self):
        return len(self.values)

    def lists(self, field):
        l = []
        for r in self.values:
            v = r.get(field)
            if v and self.restricted_indicator != v:
                l.append(v)
        return l

    def unique(self, field):
        unique_values = []
        for record in self.values:
            if record[field] not in unique_values:
                unique_values.append(record[field])

        return unique_values
