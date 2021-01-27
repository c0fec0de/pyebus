"""Dummy Server emulating EBUSD instance."""
import asyncio
import logging

from .dummy import Dummy, Quit, Stop

_LOGGER = logging.getLogger()


class DummyServer(Dummy):

    """
    Partial Dummy Server emulating EBUSD instance, just for testing.

    Keyword Args:
        port (int): Port. Default is 8888.
    """

    LOCALHOST = "127.0.0.1"

    def __init__(self, port=8888, dummydata=None):
        super().__init__(dummydata)
        self._port = port
        self._server, self._active = None, False

    def __repr__(self):
        return f"<DummyServer {self.LOCALHOST}:{self._port}>"

    @property
    def port(self):
        """Server Port."""
        return self._port

    async def async_start(self):
        """Start."""
        _LOGGER.info("%r: starting", self)

        async def _run():
            server = await asyncio.start_server(self, self.LOCALHOST, self.port)
            try:
                await server.serve_forever()
            except asyncio.CancelledError:
                pass

        self._active = True
        self._server = asyncio.create_task(_run())

    async def async_stop(self):
        """Stop."""
        if self._server:
            _LOGGER.info("%r: stopping", self)
            self._active = False
            self._server.cancel()

    async def async_wait_closed(self):
        """Wait closed."""
        if self._server:
            _LOGGER.info("%r: wait_closed", self)
            await self._server

    async def __call__(self, reader, writer):
        _LOGGER.info("%r: client connection started", self)
        while self._active:
            data = await reader.readline()
            try:
                for request in data.decode().split("\n"):
                    if request and self._active:
                        _LOGGER.info("%r: request: %r", self, request)
                        for response in self.respond(request):
                            _LOGGER.debug("%r: response: %r", self, response)
                            writer.write(f"{response}\n".encode())
                if not self._active:
                    _LOGGER.info("%r: shutdown", self)
                    writer.write("ERR: shutdown\n".encode())
            except Quit:
                break
            except Stop:
                await self.async_stop()
                break
        writer.close()
        _LOGGER.info("%r: client connection closed", self)
