import logging
import xmltodict
from .base import Base
from rets.exceptions import ParseError

logger = logging.getLogger("rets")


class CompactMetadata(Base):
    """Parses COMPCACT-DECODED RETS responses"""

    def parse(self, response, metadata_type):
        """
        Parses RETS metadata using the COMPACT-DECODED format
        :param response:
        :param metadata_type:
        :param rets_version:
        :return:
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get(metadata_type, {})
        attributes = self.get_attributes(base)

        parsed = []
        if base.get('System') or base.get('SYSTEM'):
            system_obj = {}

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


class StandardXMLetadata(Base):
    """Parses STANDARD-XML RETS responses"""

    def parse(self, response, metadata_type):
        """
        Parses RETS metadata using the STANDARD-XML format
        :param response: requests Response object
        :param metadata_type: string
        :return parsed: list
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reploy_code(xml_response_dict=xml)
        base = xml.get('RETS', {}).get('METADATA', {}).get(metadata_type, {})

        if metadata_type == 'METADATA-SYSTEM':
            syst = base.get('System', base.get('SYSTEM'))
            if not syst:
                raise ParseError("Could not get the System key from a METADATA-SYSTEM request.")

            system_obj = {}
            if syst.get('SystemID'):
                system_obj['system_id'] = str(syst['SystemID'])
            if syst.get('SystemDescription'):
                system_obj['system_description'] = str(syst['SystemDescription'])
            if syst.get('Comments'):
                system_obj['comments'] = syst['Comments']
            if base.get('@Version'):
                system_obj['version'] = base['@Version']
            return [system_obj]

        elif metadata_type == 'METADATA-CLASS':
            key = 'class'
        elif metadata_type == 'METADATA-RESOURCE':
            key = 'resource'
        elif metadata_type == 'METADATA-LOOKUP_TYPE':
            key = 'lookup'
        elif metadata_type == 'METADATA-OBJECT':
            key = 'object'
        elif metadata_type == 'METADATA-TABLE':
            key = 'field'
        else:
            msg = "Got an unknown metadata type of {0!s}".format(metadata_type)
            raise ParseError(msg)

        # Get the version with the right capitalization from the dictionary
        key_cap = None
        for k in base.keys():
            if k.lower() == key:
                key_cap = k

        if not key_cap:
            msg = 'Could not find {0!s} in the response XML'.format(key)
            raise ParseError(msg)

        if type(base[key_cap]) is list:
            return base[key_cap]
        else:
            return [base[key_cap]]
