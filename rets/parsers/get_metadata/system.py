from rets.parsers.get_metadata.base import Base
from rets.models.metadata.system import System as SysModel


class System(Base):

    @staticmethod
    def parse(rets_session, response, keyed_by):

        xml = response.xml
        base = xml.get('METADATA', {}).get('METTADATA-SYSTEM', {})

        system_obj = SysModel()
        system_obj.session = rets_session

        configuration = rets_session.configuration

        if configuration.rets_version == '1.5':
            if base.get('System', {}).get('SystemID', None) is not None:
                system_obj.system_id = str(base['System']['SystemID'])
            if base.get('System', {}).get('SystemDescription', None) is not None:
                system_obj.system_description = str(base['System']['SystemDescription'])

        else:
            if base.get('SYSTEM', {}).get('attributes', {}).get('SystemDescription', None) is not None:
                system_obj.system_id = str(base['SYSTEM']['attributes']['SystemID'])

            if base.get('SYSTEM', {}).get('attributes', {}).get('SystemDescription', None) is not None:
                system_obj.system_description = str(base['SYSTEM']['attributes']['SystemDescription'])

            if base.get('SYSTEM', {}).get('attributes', {}).get('TimeZoneOffset', None) is not None:
                system_obj.timezone_offset = str(base['SYSTEM']['attributes']['TimeZoneOffset'])

        if base.get('SYSTEM', {}).get('Comments', None) is not None:
            system_obj.comments = base['SYSTEM']['Comments']

        if base.get('attributes', {}).get('Version', None) is not None:
            system_obj.version = base['attributes']['Version']

        return system_obj
