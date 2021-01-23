"""Message Defintions."""
import collections
import copy

from anytree import NodeMixin

from .const import AUTO
from .util import repr_

_MsgDef = collections.namedtuple("_MsgDef", "circuit name read prio write update setprio")


class MsgDef(_MsgDef, NodeMixin):

    """
    Message Definition.

    A message is defined by `circuit` and `name` and has a fields

    Args:
        circuit (str): Circuit Name
        name (str): Message Name
        children (tuple): Field definitions. :any:`FieldDef` and :any:`VirtFieldDef`.

    Keyword Args:
        read (bool): Message intend to be read
        prio (int): Message Polling Priority on bus.
        write (bool): Message intend to be written
        updated (bool): Message intent to be seen automatically on every value change
        setprio: Message polling priority to be set. Integer `1-9 or `A` for automatic.

    >>> from pyebus import MsgDef, types
    >>> m = MsgDef('circuit', 'name', [
    ...     FieldDef(0, 'temp', types.IntType(-127, 128)),
    ...     FieldDef(1, 'name', types.StrType(10)),
    ...     VirtFieldDef('virt', types.StrType(), lambda msg: f'{msg.name}: {msg.temp}'),
    ... ], read=True)
    >>> m  # doctest: +ELLIPSIS
    MsgDef('circuit', 'name', (FieldDef(0, 'temp', IntType(... VirtFieldDef('virt', StrType())), read=True)
    >>> m.ident
    'circuit/name'
    >>> m.children
    (FieldDef(0, 'temp', IntType(-127, 128)), FieldDef(1, 'name', StrType(length=10)), VirtFieldDef('virt', StrType()))
    >>> m.fields
    (FieldDef(0, 'temp', IntType(-127, 128)), FieldDef(1, 'name', StrType(length=10)))
    >>> m.virtfields
    (VirtFieldDef('virt', StrType()),)
    >>> m.access
    'r----'

    :any:`MsgDef`, :any:`FieldDef` and :any:`VirtFieldDef` form a tree structure

    >>> from anytree import RenderTree
    >>> print(RenderTree(m))  # doctest: +ELLIPSIS
    MsgDef('circuit', 'name', (FieldDef(0, 'temp', IntType(-127, 128)),..., StrType())), read=True)
    ├── FieldDef(0, 'temp', IntType(-127, 128))
    ├── FieldDef(1, 'name', StrType(length=10))
    └── VirtFieldDef('virt', StrType())

    Similar object can be easily created by:

    >>> m.replace(children=m.fields[1:2])
    MsgDef('circuit', 'name', (FieldDef(1, 'name', StrType(length=10)),), read=True)
    """

    __slots__ = tuple()

    def __new__(cls, circuit, name, children, read=False, prio=None, write=False, update=False, setprio=None):
        if not read:
            prio = None
        msgdef = _MsgDef.__new__(cls, circuit, name, read, prio, write, update, setprio)
        if children:
            msgdef.children = children
        return msgdef

    def __repr__(self):
        args = (self.circuit, self.name, self.children)
        kwargs = [
            ("read", self.read, False),
            ("prio", self.prio, None),
            ("write", self.write, False),
            ("update", self.update, False),
            ("setprio", self.setprio, None),
        ]
        return repr_(self, args, kwargs)

    def __hash__(self):
        return hash(
            (self.circuit, self.name, self.children, self.read, self.prio, self.write, self.update, self.setprio)
        )

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (
                self.circuit,
                self.name,
                self.children,
                self.read,
                self.prio,
                self.write,
                self.update,
                self.setprio,
            ) == (
                other.circuit,
                other.name,
                other.children,
                other.read,
                other.prio,
                other.write,
                other.update,
                other.setprio,
            )
        else:
            return NotImplemented

    @property
    def fields(self):
        """Fields."""
        return tuple(child for child in self.children if isinstance(child, FieldDef))

    @property
    def virtfields(self):
        """Calulated Fields."""
        return tuple(child for child in self.children if isinstance(child, VirtFieldDef))

    @property
    def ident(self):
        """Identifier."""
        return f"{self.circuit}/{self.name}"

    @property
    def access(self):
        """Message Access."""
        read = "r" if self.read else "-"
        write = "w" if self.write else "-"
        update = "u" if self.update else "-"
        setprio = str(self.setprio) if self.setprio else "-"
        prio = str(self.prio) if self.prio else "-"
        return "".join((read, write, update, setprio, prio))

    def join(self, msgdef):
        """Return Joined Message Definition."""
        if (self.circuit, self.name, self.children) == (msgdef.circuit, msgdef.name, msgdef.children):
            return self.replace(
                read=self.read or msgdef.read,
                prio=self.prio or msgdef.prio,
                write=self.write or msgdef.write,
                update=self.update or msgdef.update,
                setprio=self.setprio or msgdef.setprio,
            )
        else:
            return None

    def replace(self, **kwargs):
        """Create copy with updated attributes."""
        attrs = self._asdict()
        attrs["children"] = self.children
        attrs.update(kwargs)
        # Take a copy of all children, to ensure proper tree relation
        attrs["children"] = tuple(copy.copy(fielddef) for fielddef in attrs["children"])
        return MsgDef(**attrs)


_FieldDef = collections.namedtuple("_FieldDef", "idx name type_ unit comment")


class AbstractFieldDef(_FieldDef, NodeMixin):

    """
    Abstract Field Definition.

    Args:
        idx (str): Index within Message
        name (str): Unique name (as `name` may be used multiple times by ebus)
        type_ (Type): Type

    Keyword Args:
        unit (str): Unit of the field value
        comment (str): Comment.
    """

    __slots__ = tuple()

    def __new__(cls, idx, name, type_, unit=None, comment=None):
        return _FieldDef.__new__(cls, idx, name, type_, unit or None, comment or None)

    def __repr__(self):
        args = (self.idx, self.name, self.type_)
        kwargs = [
            ("unit", self.unit, None),
            ("comment", self.comment, None),
        ]
        return repr_(self, args, kwargs)

    def _pre_detach(self, parent):
        # it is forbidden to remove fields from their message - create new one
        assert False, f"{self!r} is already used by {parent!r}"  # pragma: no cover

    @property
    def msgdef(self):
        """Message Definition."""
        return self.parent

    @property
    def ident(self):
        """Identifier."""
        return f"{self.msgdef.ident}/{self.name}" if self.msgdef else None

    def __copy__(self):
        return FieldDef(idx=self.idx, name=self.name, type_=self.type_, unit=self.unit)


class FieldDef(AbstractFieldDef):

    """
    Field Definition.

    Args:
        idx (str): Index within Message
        name (str): Unique name (as `name` may be used multiple times by ebus)
        type_ (Type): Type

    Keywords Args:
        unit (str): Unit of the field value
        comment (str): Comment.
    """


class VirtFieldDef(AbstractFieldDef):
    """
    Virtual Field Definition.

    Args:
        name (str): Unique name (as `name` may be used multiple times by ebus)
        type_ (Type): Type
        func: Function to create value.

    Keywords Args:
        unit (str): Unit of the field value
        comment (str): Comment.
    """

    def __new__(cls, name, type_, func, unit=None, comment=None):
        obj = AbstractFieldDef.__new__(cls, None, name, type_, unit or None, comment or None)
        obj.func = func
        return obj

    def __repr__(self):
        return repr_(self, (self.name, self.type_))

    def __copy__(self):
        # pylint: disable=E1101
        return VirtFieldDef(name=self.name, type_=self.type_, func=self.func, unit=self.unit, comment=self.comment)


def resolve_prio(msgdef, setprio=AUTO):
    """
    Resolve priority specification.

    Integer values are just passed through.

    >>> resolve_prio(MsgDef('circuit', 'name', [], read=True), 1)
    1
    >>> resolve_prio(MsgDef('circuit', 'name', [], read=True), 9)
    9

    The AUTO option, sets read-only messages to prio 1.

    >>> resolve_prio(MsgDef('circuit', 'name', [], read=True), AUTO)
    1

    All other readable messages get prio 2

    >>> resolve_prio(MsgDef('circuit', 'name', [], read=True, write=True), AUTO)
    2
    >>> resolve_prio(MsgDef('circuit', 'name', [], read=True, update=True), AUTO)
    2

    Non-readable messages have no prio.

    >>> resolve_prio(MsgDef('circuit', 'name', [], write=True), AUTO)
    """
    if msgdef.read:
        if setprio == AUTO:
            # Prio is only available on read messages.
            if msgdef.update or msgdef.write:
                # we just want to ensure that we do not miss any value
                setprio = 2
            else:
                setprio = 1
        return setprio
    else:
        return None
