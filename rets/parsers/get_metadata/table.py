import xmltodict

from rets.models.metadata.table import Table as TbModel
from rets.parsers.get_metadata.metadata_base import MetadataBase


class Table(MetadataBase):

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-TABLE', {})

        attributes = self.get_attributes(input_dict=base)
        for field in base['Field']:

            table_obj = TbModel(session=self.session)
            obj = self.load_from_xml(model_obj=table_obj, xml_elements=field, attributes=attributes)
            parsed[table_obj.elements['SystemName']] = obj

        return parsed
