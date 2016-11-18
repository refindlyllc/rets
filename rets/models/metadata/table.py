from rets.models.metadata.base import Base


class Table(Base):
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

    def get_lookup_values(self):
        return self.session.get_lookup_values(resource, lookup_name)