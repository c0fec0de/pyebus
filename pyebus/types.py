"""Type Engine."""
import datetime
import re

from .util import repr_


class Type:
    """Abstract Type."""

    def __init__(self):
        pass

    def __repr__(self):
        return repr_(self, self._getargs(), self._getkwargs())

    def _ident(self):
        return self._getargs(), self._getkwargs()

    def __hash__(self):
        return hash(self._ident())

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self._ident() == other._ident()
        else:
            return NotImplemented

    def _getargs(self):  # pylint: disable=R0201
        return tuple()

    def _getkwargs(self):  # pylint: disable=R0201
        return tuple()

    def with_divider(self, divider):
        """Return copy and apply `divider`."""
        raise NotImplementedError(self)

    def decode(self, value):
        """Decode `value`."""
        raise NotImplementedError(self)

    def encode(self, value):
        """Encode `value`."""
        raise NotImplementedError(self)

    @property
    def comment(self):
        """Get Comment on allowed values."""
        raise NotImplementedError(self)


class EnumType(Type):
    """
    Enumeration of `values`.

    Pure integer values are passed through, as they have an unknown coding.

    >>> t = EnumType(('on', 'auto', 'off'))
    >>> t
    EnumType(('on', 'auto', 'off'))
    >>> t.values
    ('on', 'auto', 'off')
    >>> t.comment
    'on, auto, off'

    >>> t.encode('auto')
    'auto'
    >>> t.encode(5)
    '5'
    >>> t.encode('5')
    '5'
    >>> t.encode('super')
    Traceback (most recent call last):
      ...
    ValueError: Unknown value 'super'. Allowed values are on, auto, off.
    >>> t.encode(None)
    '-'

    >>> t.decode('-') is None
    True
    >>> t.decode('auto')
    'auto'
    >>> t.decode('7')
    7
    >>> t.decode('super')
    Traceback (most recent call last):
      ...
    ValueError: Unknown value 'super'. Allowed values are on, auto, off.
    """

    _re_digit = re.compile(r"^\d+$")

    def __init__(self, values):
        super().__init__()
        self._values = values

    @property
    def values(self):
        """Enumeration Values."""
        return self._values

    def _getargs(self):
        return (self._values,)

    def decode(self, value):
        """Decode `value`."""
        if value == "-":
            value = None
        elif self._re_digit.match(value):
            value = int(value)
            # It does not matter to loop up the value, as it would have been found by ebusd
        elif value not in self._values:
            values = ", ".join(self._values)
            raise ValueError(f"Unknown value '{value}'. Allowed values are {values}.")
        return value

    def encode(self, value):
        """Encode `value`."""
        if value is None:
            value = "-"
        elif isinstance(value, int) or self._re_digit.match(str(value)):
            value = str(value)
        elif value not in self._values:
            values = ", ".join(self._values)
            raise ValueError(f"Unknown value '{value}'. Allowed values are {values}.")
        return value

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return ", ".join(self._values)


class StrType(Type):

    """
    String with optional maximum `length`.

    >>> t = StrType()
    >>> t
    StrType()
    >>> t.length is None
    True
    >>> t.encode('a string')
    'a string'
    >>> t.decode('a string')
    'a string'
    >>> t.comment is None
    True

    With length:

    >>> t = StrType(10)
    >>> t
    StrType(length=10)
    >>> t.length
    10
    >>> t.encode('a string')
    'a string'
    >>> t.decode('a string')
    'a string'
    >>> t.encode('a very long string')
    Traceback (most recent call last):
      ...
    ValueError: a very long string exceeds maximum length 10.
    >>> t.decode('a very long string')
    Traceback (most recent call last):
      ...
    ValueError: a very long string exceeds maximum length 10.
    >>> t.comment
    'Up to 10 characters'
    """

    def __init__(self, length=None):
        super().__init__()
        self._length = length

    @property
    def length(self):
        """Length."""
        return self._length

    def _getkwargs(self):
        return (("length", self.length, None),)

    def decode(self, value):
        """Decode `value`."""
        if self.length is not None and len(value) > self.length:
            raise ValueError(f"{value} exceeds maximum length {self.length}.")
        return value

    def encode(self, value):
        """Encode `value`."""
        if self.length is not None and len(value) > self.length:
            raise ValueError(f"{value} exceeds maximum length {self.length}.")
        return value

    @property
    def comment(self):
        """Get Comment on allowed values."""
        if self._length:
            return f"Up to {self._length} characters"
        else:
            return None


class HexType(Type):

    """
    Space Separated Hex Value with an optional `length` in number of Bytes.

    >>> t = HexType()
    >>> t.length is None
    True
    >>> t
    HexType()
    >>> t.decode('11 22 FF')
    (0x11, 0x22, 0xFF)
    >>> t.encode('0x11 0x22 0xFF')
    '11 22 FF'
    >>> t.encode('11 22 FF')
    '11 22 FF'
    >>> t.encode((0x11, 0x22, 0xFF))
    '11 22 FF'
    >>> t.comment
    'Hex Bytes'

    With length:

    >>> t = HexType(3)
    >>> t
    HexType(length=3)
    >>> t.length
    3
    >>> t.decode('11 22 FF')
    (0x11, 0x22, 0xFF)
    >>> t.decode('11 22')
    Traceback (most recent call last):
      ...
    ValueError: Hex value 11 22 has not expected length of 3
    >>> t.encode((0x11, 0x22, 0xFF))
    '11 22 FF'
    >>> t.encode((0x11, 0x22))
    Traceback (most recent call last):
      ...
    ValueError: Hex value (17, 34) has not expected length of 3
    >>> t.comment
    '3 Hex Bytes'
    """

    def __init__(self, length=None):
        super().__init__()
        self._length = length

    @property
    def length(self):
        """Width."""
        return self._length

    def _getkwargs(self):
        return (("length", self.length, None),)

    def decode(self, value):
        """Decode `value`."""
        values = value.split(" ")
        if self.length is not None:
            if len(values) != self.length:
                raise ValueError(f"Hex value {value} has not expected length of {self.length}")
        return tuple(Hex(int(value, 16)) for value in values)

    def encode(self, value):
        """Decode `value`."""
        if isinstance(value, str):
            value = [int(v, 16) for v in value.split(" ")]
        if self.length is not None:
            if len(value) != self.length:
                raise ValueError(f"Hex value {value} has not expected length of {self.length}")
        return " ".join((f"{v:02X}" for v in value))

    @property
    def comment(self):
        """Get Comment on allowed values."""
        if self._length:
            return f"{self._length} Hex Bytes"
        else:
            return "Hex Bytes"


class IntType(Type):

    """
    Integer in the range of [min_, max_] with granularity of `1 / divider`.

    >>> t = IntType(-4, 3)
    >>> t
    IntType(-4, 3)
    >>> t.min_
    -4
    >>> t.max_
    3
    >>> t.divider is None
    True
    >>> t.frac is None
    True
    >>> t.comment
    'Integer within [-4:3]'

    >>> t.decode('2')
    2
    >>> t.decode('-') is None
    True
    >>> t.decode('7')
    Traceback (most recent call last):
      ...
    ValueError: Value 7 exceeds upper limit of 3
    >>> t.decode('-5')
    Traceback (most recent call last):
      ...
    ValueError: Value -5 deceeds lower limit of -4

    >>> t.encode('2')
    2
    >>> t.encode(2)
    2
    >>> t.encode(None)
    '-'
    >>> t.encode(7)
    Traceback (most recent call last):
      ...
    ValueError: Value 7 exceeds upper limit of 3
    >>> t.encode(-5)
    Traceback (most recent call last):
      ...
    ValueError: Value -5 deceeds lower limit of -4

    With divider:

    >>> t = IntType(-4, 3, divider=2)
    >>> t
    IntType(-4, 3, divider=2)
    >>> t.min_
    -4
    >>> t.max_
    3
    >>> t.divider
    2
    >>> t.frac
    0.5
    >>> t.comment
    'Float within [-4:3] with 0.5 fraction'

    >>> t.decode('2')
    2.0
    >>> t.decode('-') is None
    True
    >>> t.decode('7')
    Traceback (most recent call last):
      ...
    ValueError: Value 7.0 exceeds upper limit of 3
    >>> t.decode('-5')
    Traceback (most recent call last):
      ...
    ValueError: Value -5.0 deceeds lower limit of -4

    >>> t.encode(2)
    2.0
    >>> t.encode(None)
    '-'
    >>> t.encode(7)
    Traceback (most recent call last):
      ...
    ValueError: Value 7.0 exceeds upper limit of 3
    >>> t.encode(-5)
    Traceback (most recent call last):
      ...
    ValueError: Value -5.0 deceeds lower limit of -4
    """

    def __init__(self, min_, max_, divider=None):
        super().__init__()
        self._min = min_
        self._max = max_
        self._divider = divider

    @property
    def min_(self):
        """Lower Limit."""
        return self._min

    @property
    def max_(self):
        """Upper Limit."""
        return self._max

    @property
    def divider(self):
        """Divider."""
        return self._divider

    @property
    def frac(self):
        """Fraction."""
        if self._divider and self._divider > 0:
            return 1 / self.divider
        else:
            return None

    def _getargs(self):
        return (self.min_, self.max_)

    def _getkwargs(self):
        return (("divider", self.divider, None),)

    def with_divider(self, divider):
        """Return copy and apply `divider`."""
        divider = _try_int(divider * (self.divider or 1))
        min_ = _try_int(self.min_ / divider)
        max_ = _try_int(self.max_ / divider)
        return IntType(min_, max_, divider=divider)

    def decode(self, value):
        """Decode `value`."""
        if value not in ("-", ""):
            if self.divider and self.divider > 0:
                value = float(value)
            else:
                value = int(value)
            if value < self.min_:
                raise ValueError(f"Value {value} deceeds lower limit of {self.min_}")
            if value > self.max_:
                raise ValueError(f"Value {value} exceeds upper limit of {self.max_}")
            return value
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if value is not None:
            if self.divider and self.divider > 0:
                value = float(value)
            else:
                value = int(value)
            if value < self.min_:
                raise ValueError(f"Value {value} deceeds lower limit of {self.min_}")
            if value > self.max_:
                raise ValueError(f"Value {value} exceeds upper limit of {self.max_}")
            return value
        else:
            return "-"

    @property
    def comment(self):
        """Get Comment on allowed values."""
        if self.divider and self.divider > 0:
            return f"Float within [{self.min_}:{self.max_}] with {self.frac} fraction"
        else:
            return f"Integer within [{self.min_}:{self.max_}]"


class BoolType(Type):

    """
    Boolean Type.

    >>> t = BoolType()
    >>> t
    BoolType()
    >>> t.comment
    '0 or 1'

    >>> t.decode('0')
    False
    >>> t.decode('1')
    True
    >>> t.decode('-') is None
    True

    >>> t.encode(0)
    0
    >>> t.encode(1)
    1
    >>> t.encode('0')
    0
    >>> t.encode('1')
    1
    >>> t.encode('false')
    0
    >>> t.encode('true')
    1
    >>> t.encode('FALSE')
    0
    >>> t.encode('TRUE')
    1
    >>> t.encode(None)
    '-'
    >>> t.encode('blub')
    Traceback (most recent call last):
        ...
    ValueError: blub is not a valid boolean
    """

    def decode(self, value):
        """Decode `value`."""
        if value not in ("-", ""):
            return bool(int(value))
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if value is not None:
            valuestr = str(value).lower()
            if valuestr in ("1", "true"):
                return 1
            elif valuestr in ("0", "false"):
                return 0
            else:
                raise ValueError(f"{value} is not a valid boolean")
        else:
            return "-"

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return "0 or 1"


class FloatType(Type):

    """
    Floating Type.

    >>> t = FloatType()
    >>> t
    FloatType()
    >>> t.comment
    'Float'
    >>> t.decode('-') is None
    True
    >>> t.decode('0')
    0.0
    >>> t.decode('1.456')
    1.456

    >>> t.encode(15.6)
    '15.6'
    >>> t.encode(None)
    '-'
    """

    def decode(self, value):
        """Decode `value`."""
        if value not in ("-", ""):
            value = float(value)
            return value
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if value is not None:
            value = float(value)
            return str(value)
        else:
            return "-"

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return "Float"


class DateType(Type):
    """
    Date Type.

    >>> import datetime
    >>> t = DateType()
    >>> t
    DateType()
    >>> t.comment
    'DAY.MONTH.YEAR'

    >>> t.decode('30.12.2020')
    datetime.date(2020, 12, 30)
    >>> t.decode('-.-.-') is None
    True

    >>> t.encode('30.12.2020')
    '30.12.2020'
    >>> t.encode(datetime.date(2020, 12, 30))
    '30.12.2020'
    >>> t.encode(None)
    '-.-.-'
    """

    _NONE = "-.-.-"

    def decode(self, value):
        """Decode `value`."""
        if value != self._NONE:
            return datetime.datetime.strptime(value, "%d.%m.%Y").date()
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, "%d.%m.%Y").date()
        if value is not None:
            return f"{value.day}.{value.month}.{value.year}"
        else:
            return self._NONE

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return "DAY.MONTH.YEAR"


class TimeType(Type):

    """
    Time.

    >>> t = TimeType()
    >>> t
    TimeType()
    >>> t.comment
    'HOUR:MINUTE:SECOND'
    >>> t.decode('23:59:59')
    Time(23, 59, 59)
    >>> t.decode('-:-:-') is None
    True
    >>> t.encode('23:59:59')
    '23:59:59'
    >>> t.encode(Time(23, 59, 59))
    '23:59:59'
    >>> t.encode(None)
    '-:-:-'
    """

    _NONE = "-:-:-"

    def decode(self, value):
        """Decode `value`."""
        if value != self._NONE:
            tstamp = datetime.datetime.strptime(value, "%H:%M:%S")
            return Time(tstamp.hour, tstamp.minute, tstamp.second)
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, "%H:%M:%S")
        if value is not None:
            return f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}"
        else:
            return self._NONE

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return "HOUR:MINUTE:SECOND"


class HourMinuteType(TimeType):

    """
    Time.

    Keyword Args:
        minres: Minute Resolution

    >>> t = HourMinuteType()
    >>> t
    HourMinuteType()
    >>> t.minres is None
    True
    >>> t.comment
    'HOUR:MINUTE'
    >>> t.decode('23:59')
    HourMinute(23, 59)
    >>> t.decode('-:-') is None
    True
    >>> t.encode('23:59')
    '23:59'
    >>> t.encode(HourMinute(23, 59))
    '23:59'
    >>> t.encode(None)
    '-:-'

    With Minimum Resolution

    >>> t = HourMinuteType(minres=10)
    >>> t
    HourMinuteType(minres=10)
    >>> t.minres
    10
    >>> t.comment
    'HOUR:MINUTE with 10min granularity'
    >>> t.decode('23:50')
    HourMinute(23, 50)
    >>> t.decode('-:-') is None
    True
    >>> t.decode('23:51')
    Traceback (most recent call last):
      ...
    ValueError: Minute of 23:51 must be multiple of 10
    >>> t.encode('23:50')
    '23:50'
    >>> t.encode(HourMinute(23, 50))
    '23:50'
    >>> t.encode(HourMinute(23, 52))
    Traceback (most recent call last):
      ...
    ValueError: Minute of 23:52 must be multiple of 10
    >>> t.encode(None)
    '-:-'
    """

    _NONE = "-:-"

    def __init__(self, minres=None):
        super().__init__()
        self._minres = minres

    @property
    def minres(self):
        """Minute Resolution."""
        return self._minres

    def _getkwargs(self):
        return (("minres", self._minres, None),)

    def decode(self, value):
        """Decode `value`."""
        if value != self._NONE:
            value = datetime.datetime.strptime(value, "%H:%M")
            value = HourMinute(value.hour, value.minute)
            if self._minres and (value.minute % self._minres) != 0:
                raise ValueError(f"Minute of {value} must be multiple of {self._minres}")
            return value
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, "%H:%M")
        if value is not None:
            if self._minres and (value.minute % self._minres) != 0:
                raise ValueError(f"Minute of {value} must be multiple of {self._minres}")
            return f"{value.hour:02d}:{value.minute:02d}"
        else:
            return self._NONE

    @property
    def comment(self):
        """Get Comment on allowed values."""
        if self.minres:
            return f"HOUR:MINUTE with {self._minres}min granularity"
        else:
            return "HOUR:MINUTE"


class DateTimeType(Type):

    """
    Date Time.


    >>> t = DateTimeType()
    >>> t
    DateTimeType()
    >>> t.comment
    'DAY.MONTH.YEAR HOUR:MINUTE:SECOND'
    >>> t.decode('30.12.2020 23:59:59')
    DateTime(2020, 12, 30, 23, 59, 59)
    >>> t.decode('-.-.- -:-:-') is None
    True
    >>> t.encode('30.12.2020 23:59:59')
    '30.12.2020 23:59:59'
    >>> t.encode(DateTime(2020, 12, 30, 23, 59, 59))
    '30.12.2020 23:59:59'
    >>> t.encode(None)
    '-.-.- -:-:-'
    """

    _NONE = "-.-.- -:-:-"

    def decode(self, value):
        """Decode `value`."""
        if value != self._NONE:
            return DateTime.strptime(value, "%d.%m.%Y %H:%M:%S")
        else:
            return None

    def encode(self, value):
        """Encode `value`."""
        if isinstance(value, str):
            value = DateTime.strptime(value, "%d.%m.%Y %H:%M:%S")
        if value is not None:
            return f"{value.day}.{value.month}.{value.year} {value.hour:02d}:{value.minute:02d}:{value.second:02d}"
        else:
            return self._NONE

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return "DAY.MONTH.YEAR HOUR:MINUTE:SECOND"


class WeekdayType(Type):
    """
    Weekday Type.

    >>> t = WeekdayType()
    >>> t.comment
    ''
    >>> t.decode('a')
    'a'
    >>> t.encode('a')
    'a'
    """

    def decode(self, value):
        """Decode `value`."""
        return value

    def encode(self, value):
        """Encode `value`."""
        return value

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return ""


class PinType(Type):

    """
    Pin.

    >>> t = PinType()
    >>> t.comment
    ''
    >>> t.decode('a')
    'a'
    >>> t.encode('a')
    'a'
    """

    def decode(self, value):
        """Decode `value`."""
        return value

    def encode(self, value):
        """Encode `value`."""
        return value

    @property
    def comment(self):
        """Get Comment on allowed values."""
        return ""


class DateTime(datetime.datetime):

    """
    DateTime.

    >>> t = DateTime(2020, 12, 31, 23, 59, 59)
    >>> t
    DateTime(2020, 12, 31, 23, 59, 59)
    >>> str(t)
    '31.12.2020 23:59:59'
    """

    def __str__(self):
        return self.strftime("%d.%m.%Y %H:%M:%S")


class Time(datetime.time):

    """
    Time.

    >>> t = Time(23, 59, 59)
    >>> t
    Time(23, 59, 59)
    >>> str(t)
    '23:59:59'
    """

    def __str__(self):
        return self.strftime("%H:%M:%S")


class HourMinute(datetime.time):

    """
    Time without Seconds.

    >>> t = HourMinute(23, 59)
    >>> t
    HourMinute(23, 59)
    >>> str(t)
    '23:59'
    """

    def __str__(self):
        return self.strftime("%H:%M")


class Hex(int):

    """Integer with Hex Representation."""

    def __repr__(self):
        return f"0x{self:02X}"

    __str__ = __repr__


def _try_int(value):
    intvalue = int(value)
    if float(value) == float(intvalue):
        value = intvalue
    return value
