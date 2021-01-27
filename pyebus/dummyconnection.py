"""EBUS Connection Handling."""
import collections
import logging

from .connection import CommandError, Connection, Shutdown
from .const import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT
from .dummy import Dummy

_LOGGER = logging.getLogger(__name__)


class DummyConnection(Connection, Dummy):
    """
    Dummy EBUS Connection.

    Keyword Args:
        host (str): Hostname or IP
        port (int): Port
        autoconnect (bool): Automatically connect and re-connect
        timeout (int): Connection Timeout
        dummydata (DummyData): storage for responses
    """

    def __init__(
        self, host=DEFAULT_HOST, port=DEFAULT_PORT, autoconnect=False, timeout=DEFAULT_TIMEOUT, dummydata=None
    ):
        Connection.__init__(self, host=host, port=port, autoconnect=autoconnect, timeout=timeout)
        Dummy.__init__(self, dummydata=dummydata)
        self.__connected = False
        self.__respbuffer = collections.deque()

    async def async_connect(self):
        """
        Establish connection (required before first communication).

        Raises:
            ConnectionRefusedError: If connection cannot be established
        """
        _LOGGER.debug("connect()")
        self.__connected = True

    async def async_disconnect(self):
        """Disconnect if not already done."""
        _LOGGER.debug("disconnect()")
        self.__connected = False

    def is_connected(self):
        """
        Return `True` if connection is established.

        This does not check if the connection is still usable.

        Returns:
            bool
        """
        return self.__connected

    async def _async_write(self, message):
        assert not self.__respbuffer, "Response Buffer not empty"
        self.__respbuffer.extend(self.respond(message))

    async def _async_readline(self, check=False):
        line = self.__respbuffer.popleft()
        _LOGGER.debug(f"_readline() = {line!r}")
        if line == "ERR: shutdown":
            raise Shutdown()
        if check and line.startswith("ERR: "):
            raise CommandError(line.lstrip("ERR: "))
        return line

    async def _async_ensure_connection(self):
        if not self.__connected:
            if self._autoconnect:
                await self.async_connect()
            else:
                raise ConnectionError("Not connected")
