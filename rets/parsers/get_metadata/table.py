from rets.parsers.get_metadata.base import Base
from rets.models.metadata.table import Table as TbModel
import xmltodict


class Table(Base):

    def parse(self, rets_session, response):

        xml = xmltodict.parse(response.text)
        parsed = {}

        base = xml.get('RETS', {}).get('METADATA', {}).get('METADATA-TABLE', {})

        attributes = {k.lstrip('@'): v for k, v in base.items() if k[0] == '@'}
        for field in base['Field']:

            table_obj = TbModel()
            table_obj.session = rets_session
            obj = self.load_from_xml(model_obj=table_obj, xml_elements=field, attributes=attributes)
            parsed[table_obj.elements['SystemName']] = obj

        return parsed
