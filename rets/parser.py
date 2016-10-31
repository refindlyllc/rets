import xml.etree.ElementTree as ET


def single_tier_xml_to_dict(xml_string):
    """
    Takes an XML response from the RETS client, and returns a dictionary of the keys and values. This is used in most
    of the Metadata calls
    :param xml_string: string
    :return xml_dicts: list
    """
    root = ET.fromstring(xml_string)

    objects = root[0][0]

    xml_dicts = []
    # Set Classes
    for o in objects:
        fields = {field.tag: field.text for field in o}
        xml_dicts.append(fields)

    return xml_dicts

