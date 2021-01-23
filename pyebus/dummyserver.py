"""Dummy Server emulating EBUSD instance."""
import asyncio
import collections
import logging
import re

from .dummydata import DummyData

_LOGGER = logging.getLogger()
_RE_READ = re.compile(r"read -c ([A-Za-z0-9\.]+)( -m \d+)?( -p (\d+))? ([A-Za-z0-9\.]+)")


class DummyServer:

    """
    Partial Dummy Server emulating EBUSD instance, just for testing.

    Keyword Args:
        port (int): Port. Default is 8888.
    """

    LOCALHOST = "127.0.0.1"

    def __init__(self, port=8888, dummydata=None):
        self._port = port
        self._server, self._active = None, False
        self.dummydata = dummydata or DummyData()
        self.data = collections.defaultdict(lambda: 0)
        self.prios = {}

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
                        for response in self._respond(request):
                            _LOGGER.debug("%r: response: %r", self, response)
                            writer.write(f"{response}\n".encode())
                if not self._active:
                    _LOGGER.info("%r: shutdown", self)
                    writer.write("ERR: shutdown\n".encode())
            except Exit:
                break
            except Stop:
                await self.async_stop()
                break
        writer.close()
        _LOGGER.info("%r: client connection closed", self)

    def _respond(self, request):
        if request == "quit":  # pragma: no cover
            yield "connection closed"
            yield ""
            raise Exit()
        if request == "stop":
            yield "stopping"
            yield ""
            raise Stop()

        resp = {
            "state": [self.dummydata.state],
            "info": self.dummydata.info,
            "find -a -F type,circuit,name,fields": self.dummydata.finddef,
            "find -d": self.dummydata.finddata,
            "dummyshutdown": ["ERR: shutdown"],
            "dummytrailing": ["ok", "ok2"],
        }.get(request, None)
        m_read = _RE_READ.match(request)

        if resp:
            yield from resp
        elif m_read:
            circuit, _, _, prio, name = m_read.groups()
            if prio is not None:
                self.prios[(circuit, name)] = prio
            yield str(self.data[(circuit, name)])
        elif request.startswith("write -c "):
            (circuit, name, value) = request[len("write -c ") :].split(" ")
            self.data[(circuit, name)] = value
            yield "done"
        elif request == "listen":
            if self.dummydata.listen:
                yield "listen started"
                yield ""
                yield from self.dummydata.listen
            else:
                yield "listen broken"
        else:
            yield "ERR: command not found"
            _LOGGER.error("%r: unknown request=%r", self, request)
        yield ""


class Exit(RuntimeError):

    """Exit."""


class Stop(RuntimeError):

    """Stop."""
