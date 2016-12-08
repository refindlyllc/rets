from rets.models import ResultsSet
import xmltodict
from rets.parsers.base import Base
import logging


logger = logging.getLogger('rets')


class StreamingCursor(Base):
    """
    This will stream results from the rets server, through the xml parser, to the client.
    """
    pass