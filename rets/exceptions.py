class InvalidFormat(Exception):
    """The DTD Format is Invalid"""
    pass


class RETSException(Exception):
    """The RETS Server Returned an Issue"""
    pass


class NotLoggedIn(Exception):
    """Authentication Required to Access RETS server"""
    pass


class ParseError(Exception):
    """Could not successfully Parse the RETS Response"""
    pass


class MissingVersion(Exception):
    """The RETS Version is required"""
    pass
