import logging
from rets.exceptions import RETSException, InvalidFormat

logger = logging.getLogger("rets")


class Base(object):
    """Base Parser Object"""

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

    def analyze_reploy_code(self, xml_response_dict):
        """
        Checks the RETS Response Code and handles non-zero answers.
        :param xml_response_dict:
        :return: None
        """
        if 'RETS' not in xml_response_dict:  # pragma: no cover
            raise RETSException("The <RETS> tag was expected in the response XML but it was not found.")

        attributes = self.get_attributes(input_dict=xml_response_dict['RETS'])
        if 'ReplyCode' not in attributes:  # pragma: no cover
            # The RETS server did not return a response code.
            return True

        reply_code = attributes['ReplyCode']
        reply_text = attributes.get('ReplyText', 'RETS did not supply a Reply Text.')

        logger.debug("Recieved ReplyCode of {0!s} from the RETS Server: {0!s}".format(reply_code, reply_text))
        if reply_code in ['20513','20514']:
            raise InvalidFormat(reply_text)

        if reply_code != '0':
            error_msg = '{0!s}: {1!s}'.format(reply_code, reply_text)
            raise RETSException(error_msg)
