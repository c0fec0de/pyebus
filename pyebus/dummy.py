"""Dummy Server emulating EBUSD instance."""
import collections
import logging
import re

from .dummydata import DummyData

_LOGGER = logging.getLogger()
_RE_READ = re.compile(r"read -c ([A-Za-z0-9\.]+)( -m \d+)?( -p (\d+))? ([A-Za-z0-9\.]+)")


class Dummy:

    """
    Partial Dummy Server emulating EBUSD instance, just for testing.

    Keyword Args:
        port (int): Port. Default is 8888.
    """

    def __init__(self, dummydata=None):
        self.dummydata = dummydata or DummyData()
        self.data = collections.defaultdict(lambda: 0)
        self.prios = {}
        self.notwriteable = []

    def respond(self, request):
        """Iterate over response for `request`."""
        if request == "quit":  # pragma: no cover
            yield "connection closed"
            yield ""
            raise Quit()
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
            if (circuit, name) not in self.notwriteable:
                self.data[(circuit, name)] = value
                yield "done"
            else:
                yield "ERR: not writable"
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


class Quit(RuntimeError):

    """Quit."""


class Stop(RuntimeError):

    """Stop."""
