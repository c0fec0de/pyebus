"""EBUS Messages And Their Fields."""
import collections

from .const import NA
from .util import repr_


class Msg(collections.namedtuple("_Msg", "msgdef fields")):

    """
    Message with Fields.

    The message knows its definition and its fields.
    """

    __slots__ = tuple()

    valid = True

    def __repr__(self):
        args = (self.msgdef.ident, self.fields)
        return repr_(self, args)

    @property
    def ident(self):
        """Identifier."""
        return self.msgdef.ident

    @property
    def values(self):
        """Values."""
        return tuple(field.value for field in self.fields)


class Field(collections.namedtuple("_Field", "fielddef value")):

    """
    Field with Data.

    The field knows its defintion and have one value.
    """

    __slots__ = tuple()

    def __repr__(self):
        args = (self.fielddef.name, self.value)
        return repr_(self, args)

    @property
    def ident(self):
        """Identifier."""
        return self.fielddef.ident

    @property
    def unitvalue(self):
        """Unitized Value."""
        value = self.value
        if value is not None and value is not NA and not isinstance(value, str) and self.fielddef.unit:
            return f"{value} {self.fielddef.unit}"
        else:
            return value


def filter_msg(msg=None, msgdefs=None):
    """Strip Down Message according to `msgdefs`."""
    if msg is not None:
        ident = msg.msgdef.ident
        if msgdefs is not None:
            for msgdef in msgdefs:
                if ident == msgdef.ident:
                    if msg.msgdef == msgdef:
                        return msg
                    else:
                        fields = tuple(
                            Field(field.fielddef, field.value)
                            for field in msg.fields
                            if field.fielddef in msgdef.fields
                        )
                        return Msg(msgdef, fields)
        else:
            return msg
    return None


class BrokenMsg:

    """
    Broken Message.

    A broken message failed during decoding of EBUSD or the :any:`MsgDecoder`.
    """

    valid = False

    def __init__(self, msgdef, error):
        """
        Broken Message.

        .. note: In a boolean context this instance evaluates to `False`.
        """
        self.msgdef = msgdef
        self.error = error

    def __repr__(self):
        return repr_(self, (self.msgdef.ident, self.error))

    @property
    def values(self):
        """Values."""
        return []
