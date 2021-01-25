"""Pythonic EBUS Representation."""
import asyncio
import collections
import logging

from .circuitinfodecoder import decode_circuitinfos
from .connection import CommandError, Connection
from .const import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SCANINTERVAL, DEFAULT_SCANS, DEFAULT_TIMEOUT, OK
from .msg import BrokenMsg, filter_msg
from .msgdecoder import MsgDecoder, UnknownMsgError
from .msgdef import resolve_prio
from .msgdefdecoder import decode_msgdef
from .msgdefs import MsgDefs
from .util import repr_

_LOGGER = logging.getLogger(__name__)
_CMD_FINDMSGDEFS = "find -a -F type,circuit,name,fields"


class Ebus:

    """
    Pythonic EBUS Representation.

    The EBUS handle, using one :any:`Connection` to an EBUSD instance.
    One EBUSD server can handle multiple :any:`Ebus` instances.

    Keyword Args:
        host (str): EBUSD host
        port (int): EBUSD port
        timeout (int): Connection Timeout on connect and write.
        scaninterval (str): EBUSD scan - check interval
        scans (str): EBUSD scan - number of intervals
        circuitinfos (list): List with :any:`CircuitInfo`s
        msgdefcodes (list): EBUSD Message Definition Codes
        msgdefs (MsgDefs): Message Definitions
    """

    # pylint: disable=R0902

    __slots__ = (
        "connection",
        "scaninterval",
        "scans",
        "msgdefcodes",
        "_msgdecoder",
        "_circuitinfos",
        "_circuitinfomap",
    )

    def __init__(
        self,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        timeout=DEFAULT_TIMEOUT,
        scaninterval=DEFAULT_SCANINTERVAL,
        scans=DEFAULT_SCANS,
        circuitinfos=None,
        msgdefcodes=None,
        msgdefs=None,
    ):
        self._circuitinfomap = {}
        self.connection = Connection(host=host, port=port, autoconnect=True, timeout=timeout)
        self.scaninterval = scaninterval
        self.scans = scans
        self.msgdefcodes = msgdefcodes or []
        self._msgdecoder = MsgDecoder(msgdefs or MsgDefs())
        self.circuitinfos = circuitinfos or []
        _LOGGER.info(f"{self}")

    def __repr__(self):
        return repr_(
            self,
            kwargs=(
                ("host", self.host, DEFAULT_HOST),
                ("port", self.port, DEFAULT_PORT),
                ("timeout", self.timeout, DEFAULT_TIMEOUT),
                ("scaninterval", self.scaninterval, DEFAULT_SCANINTERVAL),
                ("scans", self.scans, DEFAULT_SCANS),
            ),
        )

    @property
    def ident(self):
        """Ident."""
        return f"{self.host}:{self.port}"

    @property
    def host(self):
        """Host Name or IP."""
        return self.connection.host

    @property
    def port(self):
        """Port."""
        return self.connection.port

    @property
    def timeout(self):
        """Timeout."""
        return self.connection.timeout

    @property
    def circuitinfos(self):
        """
        Circuit Informations :any:`CircuitInfo`.

        This property is writeable.
        """
        return self._circuitinfos

    @circuitinfos.setter
    def circuitinfos(self, circuitinfos):
        self._circuitinfos = tuple(circuitinfos)
        self._circuitinfomap = dict((circuitinfo.circuit, circuitinfo) for circuitinfo in self._circuitinfos)

    def get_circuitinfo(self, circuit):
        """Return :any:`CircuitInfo` for `circuit`."""
        return self._circuitinfomap[circuit]

    @property
    def msgdefs(self):
        """
        Message Defintions :any:`MsgDefs`.

        This property is writeable.."""
        return self._msgdecoder.msgdefs

    @msgdefs.setter
    def msgdefs(self, msgdefs):
        self._msgdecoder.msgdefs = msgdefs

    def __copy__(self):
        return Ebus(
            self.host,
            self.port,
            timeout=self.timeout,
            scaninterval=self.scaninterval,
            scans=self.scans,
            circuitinfos=self.circuitinfos,
            msgdefcodes=self.msgdefcodes,
            msgdefs=self.msgdefs,
        )

    async def async_wait_scancompleted(self):
        """
        Wait until EBUSD device scan is completed.

        EBUSD scans the bus infrastructure at startup be default.
        Devices and messages are detected during this time.
        This method waits until no new message are found.
        It checks every `scaninterval` seconds.
        The number of messages has to be stable for `scans` times.

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed
            Shutdown: On EBUSD shutdown.
        """
        cnts = []
        while True:
            await self.connection.async_request(_CMD_FINDMSGDEFS)
            cnt = sum([1 async for line in self.connection.async_read()])
            cnts.append(cnt)
            if len(cnts) < self.scans or not all(cnt == cnts[-1] for cnt in cnts[-self.scans : -1]):
                await asyncio.sleep(self.scaninterval)
            else:
                break

    async def async_load_msgdefs(self):
        """
        Load Message Definitions from EBUSD.

        Alias for :any:`async_load_msgdefcodes` and :any:`decode_msgdefcodes`.

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed
            Shutdown: On EBUSD shutdown.
        """
        await self.async_load_msgdefcodes()
        self.decode_msgdefcodes()

    async def async_load_msgdefcodes(self):
        """
        Load EBUS Message Definition Codes from EBUSD and store to :any:`msgdefcodes`.

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.info("load_msgdefcodes()")
        self.msgdefcodes = msgdefcodes = []
        await self.connection.async_request(_CMD_FINDMSGDEFS)
        async for line in self.connection.async_read():
            line = line.strip()
            if line:
                try:
                    msgdef = decode_msgdef(line)
                except ValueError as exc:
                    _LOGGER.warning(f"Cannot decode message definition '{line}' ({exc})")
                if not msgdef.circuit.startswith("scan"):
                    msgdefcodes.append(line)

    def decode_msgdefcodes(self):
        """Decode `msgdefcodes` and use as `msgdefs`."""
        _LOGGER.info("decode_msgdefcodes()")
        # Decode
        msgdefs = []
        for msgdefcode in self.msgdefcodes:
            try:
                msgdefs.append(decode_msgdef(msgdefcode))
            except ValueError as exc:
                _LOGGER.warning(f"Cannot decode message definition '{msgdefcode}' ({exc})")
        # Sort
        self.msgdefs.clear()
        for msgdef in sorted(msgdefs, key=lambda msgdef: (msgdef.circuit, msgdef.name)):
            self.msgdefs.add(msgdef)

    async def async_read(self, msgdef, ttl=None, setprio=None):
        """
        Read Message.

        Args:
            msgdef (MsgDef): Message Definition

        Keyword Args:
            ttl (int): Time-to-live. Maximum age of read value in seconds.
            setprio: Priority `1-9` or `A` for automatic.

        Returns:
            Msg: Message

        Raises:
            ValueError: on decoder error
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.info(f"read({msgdef!r}, ttl={ttl!r})")
        if setprio:
            msgdef = msgdef.replace(setprio=resolve_prio(msgdef, setprio))
        return await self._async_read(msgdef, ttl)

    async def async_write(self, msgdef, value, ttl=0):
        """
        Write Message.

        If `msgdef` just contains a subset of fields, the `value` is applied only to these, by
        running a read-modify-write operation.

        Args:
            msgdef (MsgDef): Message Definition

        Keyword Args:
            ttl (int): Time-to-live. Maximum age of read value in seconds.
                       Just needed in case of a Read-Modify-Write.

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
        """
        _LOGGER.info(f"write({msgdef!r}, value={value!r}, ttl={ttl!r})")
        if not msgdef.write:
            raise ValueError(f"Message is not writeable '{msgdef}'")
        fullmsgdef = self.msgdefs.get(msgdef.circuit, msgdef.name)
        if len(fullmsgdef.children) != len(msgdef.children):
            # Read
            if not msgdef.read:
                raise ValueError(f"Message is not read-modify-writable '{msgdef}'")
            await self.connection.async_request("read", msgdef.name, c=msgdef.circuit, m=ttl)
            line = await self.connection.async_readresp(check=False)
            values = line.split(";")
            # Modify
            for fielddef in msgdef.fields:
                encvalue = fielddef.type_.encode(value)
                values[fielddef.idx] = str(encvalue)
        else:
            values = [str(fielddef.type_.encode(value)) for fielddef in msgdef.fields]
        # Write
        await self.connection.async_request("write", msgdef.name, ";".join(values), c=msgdef.circuit)
        resp = await self.connection.async_readresp()
        if resp != "done":
            raise CommandError(resp)

    async def async_listen(self, msgdefs=None):
        """
        Listen to EBUS for messages.

        Listen to automatically updated messages and EBUSDs polling mechanism.

        Keyword Args:
            msgdefs (MsgDefs): Message definitions to be listened, other messages are ignored.

        Yields:
            Msg: Messages

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.info(f"listen(msgdefs={msgdefs!r})")
        async for msg in self._async_listen(msgdefs):
            yield msg

    async def async_observe(self, msgdefs=None, ttl=None, setprio=None):
        """
        Observe `msgdefs` messages.

        Explicitly read all messages and then listen to automatically updated messages and
        EBUSDs polling mechanism.

        Keyword Args:
            msgdefs (MsgDefs): Message definitions to be observed, other messages are ignored.
            ttl (int): Time-to-live. Maximum age of read value in seconds.
            setprio: Priority `1-9` or `A` for automatic.

        Yields:
            Msg: Message

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.info(f"observe(msgdefs={msgdefs!r}, ttl={ttl!r})")
        msgdefs = msgdefs or self.msgdefs
        data = collections.defaultdict(lambda: None)

        # read all
        for msgdef in msgdefs:
            if msgdef.read:
                if setprio:
                    msgdef = msgdef.replace(setprio=resolve_prio(msgdef, setprio))
                msg = await self._async_read(msgdef, ttl=ttl)
                _LOGGER.debug("observe-read: {msg}")
                msg = filter_msg(msg, msgdefs)
                if msg:
                    if msg.valid:
                        data[msgdef.ident] = msg
                    yield msg
            elif msgdef.update:
                data[msgdef.ident] = None

        # find new values (which got updated while we where reading)
        await self.connection.async_request("find -d")
        async for line in self.connection.async_read(check=False):
            msg = self._decode_msg(line)
            _LOGGER.debug("observe-find: {msg}")
            msg = filter_msg(msg, msgdefs)
            if msg and msg != data[msg.msgdef.ident]:
                yield msg
                data[msg.msgdef.ident] = msg

        # listen
        async for msg in self._async_listen(msgdefs):
            _LOGGER.debug("observe-listen: {msg}")
            yield msg

    async def async_get_state(self):
        """
        Return state string.

        This method does **NOT** raise any exception.

        Returns:
            str: OK or any error value.
        """
        _LOGGER.info("get_state()")
        return await self._async_get_state()

    async def _async_get_state(self):
        try:
            await self.connection.async_request("state")
            state = await self.connection.async_readresp(check=False)
            if state.startswith("signal acquired"):
                return OK
            else:
                return state
        except (ConnectionError, CommandError, ConnectionRefusedError):
            return "no ebusd connection"

    async def async_is_online(self):
        """
        Return `True` if everything is fine.

        This method does **NOT** raise any exception.

        Returns:
            bool
        """
        _LOGGER.info("is_online()")
        state = await self._async_get_state()
        return state == OK

    async def async_get_info(self):
        """
        Return EBUSD meta information.

        Returns
            dict: Meta information according to metainfo_

        .. _metainfo: https://github.com/john30/ebusd/wiki/3.1.-TCP-client-commands#info
        """
        _LOGGER.info("get_info()")
        info = {}
        await self.connection.async_request("info")
        async for line in self.connection.async_read():
            name, value = line.split(":", 1)
            info[name.strip()] = value.strip()
        return info

    async def async_load_circuitinfos(self):
        """Load EBUSD Circuit Information and store in :any:`circuitinfos`."""
        _LOGGER.info("load_circuitinfos()")
        await self.connection.async_request("info")
        lines = [line async for line in self.connection.async_read()]
        self.circuitinfos = decode_circuitinfos(lines)

    async def async_cmd(self, cmd, infinite=False, check=False):
        """
        Send EBUS_Command_ `cmd` to EBUSD and Receive Response.

        .. _EBUS_Command: https://github.com/john30/ebusd/wiki/3.1.-TCP-client-commands

        Args:
            cmd (str): Commmand String

        Keyword Args:
            infinite (bool): Do not stop at first empty line.
            check (bool): Abort on `ERR:` string in response.

        Yields:
            str: response

        Raises:
            ConnectionRefusedError: If connection cannot be established
            ConnectionError: On connection breakdown.
            CommandError: If command failed and `check==True`.
            Shutdown: On EBUSD shutdown.
        """
        _LOGGER.info(f"cmd({cmd!r}, infinite={infinite!r}, check={check!r})")
        await self.connection.async_write(cmd)
        async for line in self.connection.async_read(infinite=infinite, check=check):
            yield line

    async def _async_read(self, msgdef, ttl=None):
        try:
            await self.connection.async_request("read", msgdef.name, c=msgdef.circuit, p=msgdef.setprio, m=ttl)
            line = await self.connection.async_readresp(check=False)
        except CommandError as exc:  # pragma: no cover
            return BrokenMsg(msgdef, str(exc))
        else:
            return self._msgdecoder.decode_value(msgdef, line)

    async def _async_listen(self, msgdefs):
        await self.connection.async_request("listen")
        resp = await self.connection.async_readresp()
        if resp != "listen started":
            raise CommandError(f"Listen could not be started: {resp}")
        async for line in self.connection.async_read(check=False):
            msg = self._decode_msg(line)
            msg = filter_msg(msg, msgdefs)
            if msg:
                yield msg

    def _decode_msg(self, line):
        if line:
            try:
                return self._msgdecoder.decode_line(line)
            except UnknownMsgError:
                pass
            except ValueError as exc:  # pragma: no cover
                _LOGGER.warning(f"Cannot decode message in {line!r}: {exc}")
        return None
