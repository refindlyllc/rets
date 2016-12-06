import xmltodict
from rets.models import SystemModel
from rets.parsers.base import Base


class SystemParser(Base):
    metadata_type = 'METADATA-SYSTEM'

    def __init__(self, version):
        self.version = version

    def parse(self, response):

        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA-SYSTEM', {})
        system_obj = SystemModel()

        if self.version == '1.5':
            if base.get('System', {}).get('SystemID'):
                system_obj.system_id = str(base['System']['SystemID'])
            if base.get('System', {}).get('SystemDescription'):
                system_obj.system_description = str(base['System']['SystemDescription'])

        else:
            if base.get('SYSTEM', {}).get('@SystemDescription'):
                system_obj.system_id = str(base['SYSTEM']['@SystemID'])

            if base.get('SYSTEM', {}).get('@SystemDescription'):
                system_obj.system_description = str(base['SYSTEM']['@SystemDescription'])

            if base.get('SYSTEM', {}).get('@TimeZoneOffset'):
                system_obj.timezone_offset = str(base['SYSTEM']['@TimeZoneOffset'])

        if base.get('SYSTEM', {}).get('Comments'):
            system_obj.comments = base['SYSTEM']['Comments']

        if base.get('@Version'):
            system_obj.version = base['@Version']

        return system_obj
