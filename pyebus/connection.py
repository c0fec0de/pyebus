"""EBUS Connection Handling."""
import asyncio
import logging

from .const import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT
from .util import repr_

_LOGGER = logging.getLogger(__name__)


class Connection:
    """
    EBUS Connection.

    Keyword Args:
        host (str): Hostname or IP
        port (int): Port
        autoconnect (bool): Automatically connect and re-connect
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, autoconnect=False, timeout=DEFAULT_TIMEOUT):
        self._host = host
        self._port = port
        self._autoconnect = autoconnect
        self._timeout = timeout
        self._reader, self._writer = None, None

    def __repr__(self):
        return repr_(
            self,
            kwargs=(
                ("host", self.host, DEFAULT_HOST),
                ("port", self.port, DEFAULT_PORT),
                ("autoconnect", self.autoconnect, False),
                ("timeout", self.timeout, DEFAULT_TIMEOUT),
            ),
        )

    @property
    def host(self):
        """Host."""
        return self._host

    @property
    def port(self):
        """Port."""
        return self._port

    @property
    def autoconnect(self):
        """Automatically connect and re-connect."""
        return self._autoconnect

    @property
    def timeout(self):
        """Connection Timeout."""
        return self._timeout

    async def async_connect(self):
        """
        Establish connection (required before first communication).

        Raises:
            ConnectionRefusedError: If connection cannot be established
        """
        _LOGGER.debug("connect()")
        self._reader, self._writer = await self._async_timedout(asyncio.open_connection(self._host, self._port))

    async def async_disconnect(self):
        """Disconnect if not already done."""
        _LOGGER.debug("disconnect()")
        if self._writer:
            try:
                await self._async_write("quit")
                self._writer.close()
                await self._writer.wait_closed()
            except BrokenPipeError:  # pragma: no cover
                pass
            finally:
                self._reader, self._writer = None, None

    def is_connected(self):
        """
        Return `True` if connection is established.

        This does not check if the connection is still usable.

        Returns:
            bool
        """
        return self._writer is not None and not self._writer.is_closing()

    async def async_write(self, message):
        """
        Send TCP `message` to EBUSD.

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: If not connected (`autoconnect==False`)
        """
        _LOGGER.debug(f"write({message!r})")
        await self._async_ensure_connection()
        await self._async_write(message)

    async def async_request(self, cmd, *args, **kwargs):
        """
        Assemble request starting with `cmd` and position `args` and keywords `kwargs'.

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: If not connected (`autoconnect==False`)
        """
        parts = [cmd]
        parts += [f"-{option} {value}" for option, value in kwargs.items() if value is not None]
        parts += [str(arg) for arg in args]
        message = " ".join(parts)
        _LOGGER.debug(f"request({message!r})")
        await self._async_ensure_connection()
        await self._async_write(message)

    async def async_read(self, infinite=False, check=True):
        """
        Receive lines until an empty one (`infinite==False`) or infinitly (`infinite==True`).

        Yields:
            str: line read

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: If not connected (`autoconnect==False`)
            CommandError: If command failed (`check==True`)
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.debug(f"read(infinite={infinite!r}, check={check!r})")
        await self._async_ensure_connection()
        while True:
            line = await self._async_readline(check=check)
            if not line and not infinite:
                break
            yield line

    async def async_readresp(self, check=True):
        """
        Receive command response.

        Read one line as command response and one empty line.

        Returns:
            str: response

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: If not connected (`autoconnect==False`)
            CommandError: If command failed (`check==True`) or trailing data.
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.debug(f"readresp(check={check!r})")
        await self._async_ensure_connection()
        line = await self._async_readline(check=check)
        empty = await self._async_readline()
        if empty:
            raise CommandError(f"Trailing data {empty}")
        return line

    async def _async_write(self, message):
        self._writer.write(f"{message}\n".encode())
        await self._async_timedout(self._writer.drain())

    async def _async_readline(self, check=False):
        line = await self._reader.readline()
        line = line.decode("utf-8").rstrip()
        _LOGGER.debug(f"_readline() = {line!r}")
        if line == "ERR: shutdown":
            raise Shutdown()
        if check and line.startswith("ERR: "):
            raise CommandError(line.lstrip("ERR: "))
        return line

    async def _async_ensure_connection(self):
        if not self._writer or self._writer.is_closing():
            if self._autoconnect:
                await self.async_connect()
            else:
                raise ConnectionError("Not connected")

    async def _async_timedout(self, task):
        if self._timeout:
            try:
                result = await asyncio.wait_for(task, timeout=self._timeout)
            except asyncio.TimeoutError as timeout:
                raise ConnectionError(f"{self.host}:{self.port} timeout") from timeout
        else:
            result = await task
        return result


class CommandError(RuntimeError):

    """Command Error raised in case of EBUSD error, typically if the response starts with `ERR:`"""


class Shutdown(ConnectionError):

    """EBUS Shutdown."""
