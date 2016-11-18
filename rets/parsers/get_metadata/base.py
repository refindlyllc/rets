

class Base(object):

    @staticmethod
    def load_from_xml(model_obj, xml_elements, attributes=None):
        for attr in model_obj.attributes:
            if attr in attributes:
                model_obj.attributes[attr] = attributes[attr]

        for elem in model_obj.elements:
            if elem in xml_elements:
                model_obj.elements[elem] = xml_elements[elem]

        return model_obj
