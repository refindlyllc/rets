import logging
import xmltodict
from .base import Base

logger = logging.getLogger("rets")


class Metadata(Base):

    def parse(self, response, metadata_type, rets_version=None):
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get(metadata_type, {})
        attributes = self.get_attributes(base)

        parsed = []
        if base.get('System') or base.get('SYSTEM'):
            system_obj = {}
            if rets_version == '1.5':
                if base.get('System', {}).get('SystemID'):
                    system_obj['system_id'] = str(base['System']['SystemID'])
                if base.get('System', {}).get('SystemDescription'):
                    system_obj['system_description'] = str(base['System']['SystemDescription'])

            else:
                if base.get('SYSTEM', {}).get('@SystemDescription'):
                    system_obj['system_id'] = str(base['SYSTEM']['@SystemID'])

                if base.get('SYSTEM', {}).get('@SystemDescription'):
                    system_obj['system_description'] = str(base['SYSTEM']['@SystemDescription'])

                if base.get('SYSTEM', {}).get('@TimeZoneOffset'):
                    system_obj['timezone_offset'] = str(base['SYSTEM']['@TimeZoneOffset'])

            if base.get('SYSTEM', {}).get('Comments'):
                system_obj['comments'] = base['SYSTEM']['Comments']

            if base.get('@Version'):
                system_obj['version'] = base['@Version']

            parsed.append(system_obj)

        elif 'DATA' in base:
            if type(base['DATA']) is not list:  # xmltodict could take single entry XML lists and turn them into str
                base['DATA'] = [base['DATA']]

            for data in base['DATA']:
                data_dict = self.data_columns_to_dict(columns_string=base.get('COLUMNS', ''), dict_string=data)
                data_dict.update(attributes)
                parsed.append(data_dict)

        return parsed
