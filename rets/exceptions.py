class RETSException(Exception):
    """The RETS Server Returned an Issue"""
    def __init__(self, reply_text=None, reply_code=None):
        self.reply_code = reply_code
        self.reply_text = reply_text

    def __repr__(self):
        return self.reply_text

    def __str__(self):
        return self.reply_text


class HTTPException(Exception):
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


class MaxrowException(Exception):
    """The RETS Servers truncated the results with a <MAXROW/>"""
    def __init__(self, rows_returned):
        self.rows_returned = rows_returned
