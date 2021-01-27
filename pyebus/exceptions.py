"""Exceptions."""


class UnknownMsgError(RuntimeError):

    """Exception raised in case of unknown Message."""


class CommandError(RuntimeError):

    """Command Error raised in case of EBUSD error, typically if the response starts with `ERR:`"""


class Shutdown(ConnectionError):

    """EBUS Shutdown."""
