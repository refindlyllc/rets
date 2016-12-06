

class ResultsSet(object):

    def __repr__(self):
        return '<ResultsSet: {} Found in {}:{} for {}>'.format(self.total_results_count,
                                                            self.resource.StandardName,
                                                            self.resource_class,
                                                            self.dmql)

    def __len__(self):
        return len(self.values)

    def __init__(self):
        self.metadata = None
        self.resource = None
        self.resource_class = None
        self.returned_results_count = 0
        self.total_results_count = 0
        self.values = []
        self.headers = {}
        self.restricted_indicator = '****'
        self.max_rows_reached = False
        self.dmql = None

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