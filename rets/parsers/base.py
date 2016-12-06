import logging
import json
logger = logging.getLogger("rets")


class Base(object):

    @staticmethod
    def get_attributes(input_dict):
        return {k.lstrip("@"): v for k, v in input_dict.items() if k[0] == "@"}

    @staticmethod
    def data_columns_to_dict(columns_string, dict_string, delimiter=None):
        if delimiter:
            return {k: v for k, v in zip(columns_string.split(delimiter), dict_string.split(delimiter))}
        else:
            return {k: v for k, v in zip(columns_string.split(), dict_string.split())}

    def analyze_reploy_code(self, xml_response_dict):
        if 'RETS' not in xml_response_dict:
            raise RuntimeError("I should raise something here too")

        attributes = self.get_attributes(input_dict=xml_response_dict['RETS'])
        if 'ReplyCode' not in attributes:
            # The RETS server did not return a response code.
            return True

        reply_code = attributes['ReplyCode']
        reply_text = attributes.get('ReplyText', 'RETS did not supply a Reply Text.')

        logger.debug("Recieved ReplyCode of {0!s} from the RETS Server: {0!s}".format(reply_code, reply_text))
        if reply_code != '0':
            raise RuntimeError("I feel like we should raise something here")
