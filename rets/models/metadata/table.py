from .base_model import BaseModel


class TableModel(BaseModel):

    def __init__(self, elements=None, attributes=None):
        self.SystemName = None
        self.StandardName = None
        self.LongName = None
        self.DBName = None
        self.ShortName = None
        self.MaximumLength = None
        self.DataType = None
        self.Precision = None
        self.Searchable = None
        self.Interpretation = None
        self.Alignment = None
        self.UseSeparator = None
        self.EditMaskID = None
        self.LookupName = None
        self.MaxSelect = None
        self.Units = None
        self.Index = None
        self.Minimum = None
        self.Maximum = None
        self.Default = None
        self.Required = None
        self.SearchHelpID = None
        self.Unique = None
        self.MetadataEntryID = None
        self.ModTimeStamp = None
        self.ForeignKeyName = None
        self.ForeignField = None
        self.InKeyIndex = None
        self.Version = None
        self.Date = None
        self.Resource = None
        self.Class = None

        self.load_elements_and_attributes(elements=elements, attributes=attributes)

    def __repr__(self):
        return '<Table Metadata: {}>'.format(self.SystemName)

    @property
    def resource(self):
        return self.Resource

    @property
    def lookup_name(self):
        return self.LookupName
