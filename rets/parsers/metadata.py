import logging

import xmltodict

from rets.exceptions import ParseError
from .base import Base

logger = logging.getLogger("rets")


class CompactMetadata(Base):
    """Parses COMPCACT-DECODED RETS responses"""

    def parse(self, response, metadata_type):
        """
        Parses RETS metadata using the COMPACT-DECODED format
        :param response:
        :param metadata_type:
        :return:
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reply_code(xml_response_dict=xml)
        base = xml.get("RETS", {}).get(metadata_type, {})
        attributes = self.get_attributes(base)

        if base.get("System") or base.get("SYSTEM"):
            system_obj = {}

            if base.get("SYSTEM", {}).get("@SystemDescription"):
                system_obj["system_id"] = str(base["SYSTEM"]["@SystemID"])

            if base.get("SYSTEM", {}).get("@SystemDescription"):
                system_obj["system_description"] = str(
                    base["SYSTEM"]["@SystemDescription"]
                )

            if base.get("SYSTEM", {}).get("@TimeZoneOffset"):
                system_obj["timezone_offset"] = str(base["SYSTEM"]["@TimeZoneOffset"])

            if base.get("SYSTEM", {}).get("Comments"):
                system_obj["comments"] = base["SYSTEM"]["Comments"]

            if base.get("@Version"):
                system_obj["version"] = base["@Version"]

            yield system_obj

        elif "DATA" in base:
            if not isinstance(
                base["DATA"], list
            ):  # xmltodict could take single entry XML lists and turn them into str
                base["DATA"] = [base["DATA"]]

            for data in base["DATA"]:
                data_dict = self.data_columns_to_dict(
                    columns_string=base.get("COLUMNS", ""), dict_string=data
                )
                data_dict.update(attributes)

                yield data_dict



class StandardXMLMetadata(Base):
    """Parses STANDARD-XML RETS responses"""

    @staticmethod
    def _identify_key(some_dict, some_key):
        # Get the version with the right capitalization from the dictionary
        key_cap = None
        for k in some_dict.keys():
            if k.lower() == some_key:
                key_cap = k
            # Some servers don't index lookup correctly for the given RETS version; let's address that here
            elif some_key == "lookuptype":
                if k.lower() == "lookup":
                    key_cap = k

        if not key_cap:
            msg = "Could not find {0!s} in the response XML".format(some_key)
            raise ParseError(msg)
        return key_cap

    def parse(self, response, metadata_type):
        """
        Parses RETS metadata using the STANDARD-XML format
        :param response: requests Response object
        :param metadata_type: string
        :return parsed: list
        """
        xml = xmltodict.parse(response.text)
        self.analyze_reply_code(xml_response_dict=xml)
        base = xml.get("RETS", {}).get("METADATA", {}).get(metadata_type, {})

        if metadata_type == "METADATA-SYSTEM":
            syst = base.get("System", base.get("SYSTEM"))
            if not syst:
                raise ParseError(
                    "Could not get the System key from a METADATA-SYSTEM request."
                )

            system_obj = {}
            if syst.get("SystemID"):
                system_obj["system_id"] = str(syst["SystemID"])
            if syst.get("SystemDescription"):
                system_obj["system_description"] = str(syst["SystemDescription"])
            if syst.get("Comments"):
                system_obj["comments"] = syst["Comments"]
            if base.get("@Version"):
                system_obj["version"] = base["@Version"]
            return [system_obj]

        elif metadata_type == "METADATA-CLASS":
            key = "class"
        elif metadata_type == "METADATA-RESOURCE":
            key = "resource"
        elif metadata_type == "METADATA-LOOKUP_TYPE":
            key = "lookuptype"
        elif metadata_type == "METADATA-OBJECT":
            key = "object"
        elif metadata_type == "METADATA-TABLE":
            key = "field"
        else:
            msg = "Got an unknown metadata type of {0!s}".format(metadata_type)
            raise ParseError(msg)

        if isinstance(base, list):
            # Multiple resources were returned. Often the result of a wildcard request.
            # Return dict of lists
            res = {}
            for i in base:
                key_cap = self._identify_key(i, key)
                res[i["@Lookup"]] = i[key_cap]
            return res

        else:
            key_cap = self._identify_key(base, key)
            # Server returns single list
            if isinstance(base[key_cap], list):
                return base[key_cap]
            else:
                return [base[key_cap]]
