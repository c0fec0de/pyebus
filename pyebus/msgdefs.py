"""Message Defintions."""
import collections
import re
from fnmatch import fnmatch

from .const import AUTO
from .msgdef import resolve_prio

_RE_RESOLVE = re.compile(r"\A([^/#+]+)/([^/#+]+)(#(\d|A))?(/([^/#]*))?\Z")


class Pattern(collections.namedtuple("Pattern", "circuit name setprio fieldname")):

    """Message Definition and Field Definition Search Pattern."""

    @staticmethod
    def from_str(pattern):
        """Create :any:`Pattern` from `pattern` string."""
        mat = _RE_RESOLVE.fullmatch(pattern)
        if mat:
            circuit, name, _, setprio, _, fieldname = mat.groups()
            return Pattern(circuit, name, setprio, fieldname)
        else:
            return None


class MsgDefs:

    """
    Message Definitions Container.

    >>> from .msgdef import MsgDef, FieldDef
    >>> from .types import Type
    >>> msgdefs = MsgDefs()
    >>> msgdefs.add(MsgDef('mc', 'Status0a', (
    ...     FieldDef(0, 'temp', Type(), '°C'),
    ...     FieldDef(1, 'mixer', Type(), None),
    ...     FieldDef(2, 'onoff-0', Type(), None),
    ...     FieldDef(3, 'onoff-1', Type(), None),
    ...     FieldDef(4, 'temp0', Type(), '°C'),
    ... ), read=True))
    >>> msgdefs.add(MsgDef('hc', 'Status0', (
    ...     FieldDef(0, 'temp', Type(), '°C'),
    ...     FieldDef(1, 'temp0', Type(), '°C'),
    ... ), read=True))
    >>> msgdefs.get('mc', 'Status0a')
    MsgDef('mc', 'Status0a', (FieldDef(0, 'temp', ...'°C'), FieldDef(1, 'mixer', ..., unit='°C')), read=True)
    >>> list(msgdefs)
    [MsgDef('mc', 'Status0a', (FieldDef(0, 'temp', ...'°C'), FieldDef(1, 'mixer', ..., unit='°C')), read=True)]
    >>> msgdefs.summary()
    '2 messages (2 read, 0 update, 0 write) with 7 fields'
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """Remove All Stored Message Definitions."""
        self._msgdefs = collections.defaultdict(lambda: collections.defaultdict(list))

    def add(self, msgdef):
        """Add Message Definition."""
        msgdefs = self._msgdefs[msgdef.circuit][msgdef.name]
        for idx, msgdef0 in enumerate(msgdefs):
            joined = msgdef0.join(msgdef)
            if joined is not None:
                msgdefs[idx] = joined
                break
        else:
            msgdefs.append(msgdef)

    def get(self, circuit, name):
        """
        Get message with `circuit` and `name`.

        Returns
            MsgDef: Message Definition
        """
        msgdefs = self._msgdefs
        if circuit in msgdefs:
            circuitmsgdefs = msgdefs[circuit]
            if name in circuitmsgdefs:
                return circuitmsgdefs[name][0]
        return None

    def get_ident(self, ident):
        """
        Get message with `ident`.

        Returns
            MsgDef: Message Definition
        """
        pat = Pattern.from_str(ident)
        if pat:
            return self.get(pat.circuit, pat.name)
        return None

    def find(self, circuit, name="*"):
        """
        Find all message definitions matching `circuit` and `name`, wildcards and placeholder are accepted.

        Returns:
            MsgDefs: Message Definitions
        """
        msgdefs = MsgDefs()
        circuit = circuit.lower()
        name = name.lower()
        for msgdef in self:
            if fnmatch(msgdef.circuit.lower(), circuit) and fnmatch(msgdef.name.lower(), name):
                msgdefs.add(msgdef)
        return msgdefs

    def resolve(self, patterns, filter_=None):
        """
        Resolve patterns and filter message definitions.

        Returns:
            MsgDefs: Message Definitions
        """
        if isinstance(patterns, str):
            patterns = patterns.split(";")
        msgdefs = MsgDefs()
        for pattern in patterns:
            for msgdef in self._resolve(pattern.strip()):
                if msgdef not in msgdefs and (filter_ is None or filter_(msgdef)):
                    msgdefs.add(msgdef)
        return msgdefs

    def _resolve(self, pattern):
        pat = Pattern.from_str(pattern)
        if pat:
            circuit, name, setprio, fieldname = pat
            for msgdef in self.find(circuit, name):
                if fieldname is None:
                    fields = msgdef.children
                else:
                    fields = tuple(
                        fielddef for fielddef in msgdef.children if fnmatch(fielddef.name.lower(), fieldname.lower())
                    )
                if not fields:
                    continue
                if fields == msgdef.children and (setprio is None or not msgdef.read):
                    yield msgdef
                else:
                    setprio = setprio if setprio in (AUTO, None) else int(setprio)
                    yield msgdef.replace(children=fields, setprio=setprio)
        else:
            raise ValueError(f"Invalid pattern {pattern!r}")

    def set_defaultprio(self, defaultprio):
        """Set Priorities of all messages without a priority value."""
        msgdefs = self._msgdefs
        for circuitmsgdefs in msgdefs.values():
            for msgdefs in circuitmsgdefs.values():
                for idx, msgdef in enumerate(msgdefs):
                    if msgdef.setprio is None:
                        msgdefs[idx] = msgdef.replace(setprio=resolve_prio(msgdef, msgdef.setprio or defaultprio))

    def summary(self):
        """
        Summary.

        Returns:
            str: Summary.
        """
        total = len(self)
        fields = sum(len(msgdef.children) for msgdef in self)
        read = sum([1 for msgdef in self if msgdef.read])
        update = sum([1 for msgdef in self if msgdef.update])
        write = sum([1 for msgdef in self if msgdef.write])
        return f"{total} messages ({read} read, {update} update, {write} write) with {fields} fields"

    def __iter__(self):
        for circuitmsgdefs in self._msgdefs.values():
            for msgdefs in circuitmsgdefs.values():
                yield from msgdefs

    def __len__(self):
        return sum(
            sum(len(msgdefs) for msgdefs in circuitmsgdefs.values()) for circuitmsgdefs in self._msgdefs.values()
        )

    def __add__(self, other):
        if self.__class__ is other.__class__:
            msgdefs = MsgDefs()
            for msgdef in self:
                msgdefs.add(msgdef)
            for msgdef in other:
                msgdefs.add(msgdef)
            return msgdefs
        else:
            return NotImplemented

    def __sub__(self, other):
        if self.__class__ is other.__class__:
            msgdefs = MsgDefs()
            othermsgs = tuple(other)
            for msgdef in self:
                if msgdef not in othermsgs:
                    msgdefs.add(msgdef)
            return msgdefs
        else:
            return NotImplemented
