import logging
import xmltodict
from rets.exceptions import RETSException
logger = logging.getLogger("rets")


class Base(object):

    @staticmethod
    def get_attributes(input_dict):
        """
        Get attributes of xml tags in input_dict and creates a dictionary with the attribute name as the key and the
        attribute value as the value
        :param input_dict: The xml tag with the attributes and values
        :return: dict
        """
        return {k.lstrip("@"): v for k, v in input_dict.items() if k[0] == "@"}

    @staticmethod
    def data_columns_to_dict(columns_string, dict_string, delimiter=None):
        """
        Turns column names in a single string into a dictionary with the key being the column name and the value
        being the value in that column for each row
        :param columns_string: A string of column names
        :param dict_string: A string of values
        :param delimiter: The delimiter to use to split the column and values
        :return: dict
        """
        if delimiter:
            return {k: v for k, v in zip(columns_string.split(delimiter), dict_string.split(delimiter))}
        else:
            return {k: v for k, v in zip(columns_string.split(), dict_string.split())}

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

    def analyze_reploy_code(self, xml_response_dict):
        if 'RETS' not in xml_response_dict:
            raise RETSException("The <RETS> tag was expected in the response XML but it was not found.")

        attributes = self.get_attributes(input_dict=xml_response_dict['RETS'])
        if 'ReplyCode' not in attributes:
            # The RETS server did not return a response code.
            return True

        reply_code = attributes['ReplyCode']
        reply_text = attributes.get('ReplyText', 'RETS did not supply a Reply Text.')

        logger.debug("Recieved ReplyCode of {0!s} from the RETS Server: {0!s}".format(reply_code, reply_text))
        if reply_code != '0':
            error_msg = '{0!s}: {1!s}'.format(reply_code, reply_text)
            raise RETSException(error_msg)
