from .base import Base


class TableModel(Base):
    elements = {
        'SystemName': None,
        'StandardName': None,
        'LongName': None,
        'DBName': None,
        'ShortName': None,
        'MaximumLength': None,
        'DataType': None,
        'Precision': None,
        'Searchable': None,
        'Interpretation': None,
        'Alignment': None,
        'UseSeparator': None,
        'EditMaskID': None,
        'LookupName': None,
        'MaxSelect': None,
        'Units': None,
        'Index': None,
        'Minimum': None,
        'Maximum': None,
        'Default': None,
        'Required': None,
        'SearchHelpID': None,
        'Unique': None,
        'MetadataEntryID': None,
        'ModTimeStamp': None,
        'ForeignKeyName': None,
        'ForeignField': None,
        'InKeyIndex': None,
    }

    attributes = {
        'Version': None,
        'Date': None,
        'Resource': None,
        'Class': None,
    }

    lookup_values = None

    def __repr__(self):
        return '<Table Metadata: {}>'.format(self.elements['SystemName'])

    @property
    def resource(self):
        return self.attributes['Resource']

    @property
    def lookup_name(self):
        return self.elements['LookupName']
