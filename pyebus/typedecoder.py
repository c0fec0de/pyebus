"""EBUSD Typecode Decoder."""
import re

from . import types

_RE_BIT = re.compile(r"\ABI\d(:(\d))?\Z")

TYPEMAP = {
    # BDA       BCD date                      dd.mm.yyyy               day first, including weekday, Sunday=0x06
    # BDA:3     BCD date                      dd.mm.yyyy               day first, excluding weekday
    # HDA       hex date                      dd.mm.yyyy               day first, including weekday, Sunday=0x07
    # HDA:3     hex date                      dd.mm.yyyy               day first, excluding weekday
    # DAY       date in days                  dd.mm.yyyy               days since 01.01.1900
    "BDA": types.DateType(),
    "BDA:3": types.DateType(),
    "HDA": types.DateType(),
    "HDA:3": types.DateType(),
    "DAY": types.DateType(),
    # BTI       BCD time                      hh:mm:ss                 seconds first
    # HTI       hex time                      hh:mm:ss                 hours first
    # VTI       hex time                      hh:mm:ss                 seconds first
    "BTI": types.TimeType(),
    "HTI": types.TimeType(),
    "VTI": types.TimeType(),
    # BTM       BCD time                      hh:mm                    minutes first
    # HTM       hex time                      hh:mm                    hours first
    # VTM       hex time                      hh:mm                    minutes first
    # MIN       time in minutes               hh:mm                    minutes since last midnight
    # TTM       truncated time                hh:m0                    multiple of 10 minutes
    # TTH       truncated time                hh:m0                    multiple of 30 minutes
    # TTQ       truncated time                hh:mm                    multiple of 15 minutes
    "BTM": types.HourMinuteType(),
    "HTM": types.HourMinuteType(),
    "VTM": types.HourMinuteType(),
    "MIN": types.HourMinuteType(),
    "TTM": types.HourMinuteType(minres=10),
    "TTH": types.HourMinuteType(minres=30),
    "TTQ": types.HourMinuteType(minres=15),
    # BDY       weekday                       Mon...Sun                Sunday=0x06
    # HDY       weekday                       Mon...Sun                Sunday=0x07
    "BDY": types.WeekdayType(),
    "HDY": types.WeekdayType(),
    # BCD       unsigned BCD                  0...99
    # BCD:2     unsigned BCD                  0...9999
    # BCD:3     unsigned BCD                  0...999999
    # BCD:4     unsigned BCD                  0...99999999
    "BCD": types.IntType(0, 99),
    "BCD:2": types.IntType(0, 9999),
    "BCD:3": types.IntType(0, 999999),
    "BCD:4": types.IntType(0, 99999999),
    # TODO: HCD       unsigned hex BCD              0...99999999             each BCD byte converted to hex
    # TODO: HCD:1     unsigned hex BCD              0...99                   each BCD byte converted to hex
    # TODO: HCD:2     unsigned hex BCD              0...9999                 each BCD byte converted to hex
    # TODO: HCD:3     unsigned hex BCD              0...999999               each BCD byte converted to hex
    # PIN       unsigned BCD                  0000...9999
    "PIN": types.PinType(),
    # UCH       unsigned integer              0...254
    "UCH": types.IntType(0, 254),
    # SCH       signed integer               -127...127
    # D1B       signed integer               -127...127
    "SCH": types.IntType(-127, 127),
    "D1B": types.IntType(-127, 127),
    # D1C       unsigned number               0.0...100.0              fraction 1/2 = divisor 2
    "D1C": types.IntType(0, 100, divider=2),
    # D2B       signed number                -127.99...127.99          fraction 1/256 = divisor 256
    "D2B": types.IntType(-127.99, 127.99, divider=256),
    # D2C       signed number                -2047.9...2047.9          fraction 1/16 = divisor 16
    "D2C": types.IntType(-2047.9, 2047.9, divider=16),
    # FLT       signed number                -32.767...32.767         low byte first, fraction 1/1000 = divisor 1000
    # FLR       signed number reverse        -32.767...32.767         high byte first, fraction 1/1000 = divisor 1000
    "FLT": types.IntType(-32.767, 32.767, divider=1000),
    "FLR": types.IntType(-32.767, 32.767, divider=1000),
    # EXP       signed float number          -3.0e38...3.0e38          low byte first
    # EXR       signed float number reverse  -3.0e38...3.0e38          high byte first
    "EXP": types.FloatType(),
    "EXR": types.FloatType(),
    # UIN       unsigned integer              0...65534                low byte first
    # UIR       unsigned integer reverse      0...65534                high byte first
    "UIN": types.IntType(0, 65534),
    "UIR": types.IntType(0, 65534),
    # SIN       signed integer               -32767...32767            low byte first
    # SIR       signed integer reverse       -32767...32767            high byte first
    "SIN": types.IntType(-32767, 32767),
    "SIR": types.IntType(-32767, 32767),
    # U3N       unsigned 3 byte int           0...16777214             low byte first
    # U3R       unsigned 3 byte int reverse   0...16777214             high byte first
    "U3N": types.IntType(0, 16777214),
    "U3R": types.IntType(0, 16777214),
    # S3N       signed 3 byte int            -8388607...8388607        low byte first
    # S3R       signed 3 byte int reverse    -8388607...8388607        high byte first
    "S3N": types.IntType(-8388607, 8388607),
    "S3R": types.IntType(-8388607, 8388607),
    # ULG       unsigned integer              0...4294967294           low byte first
    # ULR       unsigned integer reverse      0...4294967294           high byte first
    "ULG": types.IntType(0, 4294967294),
    "ULR": types.IntType(0, 4294967294),
    # SLG       signed integer               -2147483647...2147483647  low byte first
    # SLR       signed integer reverse       -2147483647...2147483647  high byte first
    "SLG": types.IntType(-2147483647, 2147483647),
    "SLR": types.IntType(-2147483647, 2147483647),
}


def decode_type(typecode, divider=None):
    """
    Get :any:`Type` instance for `typecode`.

    Args:
        typecode: Type code according to typecodes_

    Keyword Args:
        divider (int): Additional divider.

    .. _typecodes: https://github.com/john30/ebusd/wiki/4.3.-Builtin-data-types

    >>> decode_type("STR:*")
    StrType()
    >>> decode_type("STR:9")
    StrType(length=9)
    >>> decode_type("HEX:*")
    HexType()
    >>> decode_type("HEX:9")
    HexType(length=9)
    >>> decode_type("BI0:0")
    BoolType()
    >>> decode_type("BI0:7")
    BoolType()
    >>> decode_type("BDA")
    DateType()
    >>> decode_type("BDA:3")
    DateType()
    >>> decode_type("HDA")
    DateType()
    >>> decode_type("HDA:3")
    DateType()
    >>> decode_type("DAY")
    DateType()
    >>> decode_type("BTI")
    TimeType()
    >>> decode_type("HTI")
    TimeType()
    >>> decode_type("VTI")
    TimeType()
    >>> decode_type("BTM")
    HourMinuteType()
    >>> decode_type("HTM")
    HourMinuteType()
    >>> decode_type("VTM")
    HourMinuteType()
    >>> decode_type("MIN")
    HourMinuteType()
    >>> decode_type("TTM")
    HourMinuteType(minres=10)
    >>> decode_type("TTH")
    HourMinuteType(minres=30)
    >>> decode_type("TTQ")
    HourMinuteType(minres=15)
    >>> decode_type("BDY")
    WeekdayType()
    >>> decode_type("HDY")
    WeekdayType()
    >>> decode_type("BCD")
    IntType(0, 99)
    >>> decode_type("BCD:2")
    IntType(0, 9999)
    >>> decode_type("BCD:3")
    IntType(0, 999999)
    >>> decode_type("BCD:4")
    IntType(0, 99999999)
    >>> decode_type("PIN")
    PinType()
    >>> decode_type("UCH")
    IntType(0, 254)
    >>> decode_type("SCH")
    IntType(-127, 127)
    >>> decode_type("D1B")
    IntType(-127, 127)
    >>> decode_type("D1C")
    IntType(0, 100, divider=2)
    >>> decode_type("D2B")
    IntType(-127.99, 127.99, divider=256)
    >>> decode_type("D2C")
    IntType(-2047.9, 2047.9, divider=16)
    >>> decode_type("FLT")
    IntType(-32.767, 32.767, divider=1000)
    >>> decode_type("FLR")
    IntType(-32.767, 32.767, divider=1000)
    >>> decode_type("EXP")
    FloatType()
    >>> decode_type("EXR")
    FloatType()
    >>> decode_type("UIN")
    IntType(0, 65534)
    >>> decode_type("UIR")
    IntType(0, 65534)
    >>> decode_type("SIN")
    IntType(-32767, 32767)
    >>> decode_type("SIR")
    IntType(-32767, 32767)
    >>> decode_type("U3N")
    IntType(0, 16777214)
    >>> decode_type("U3R")
    IntType(0, 16777214)
    >>> decode_type("S3N")
    IntType(-8388607, 8388607)
    >>> decode_type("S3R")
    IntType(-8388607, 8388607)
    >>> decode_type("ULG")
    IntType(0, 4294967294)
    >>> decode_type("ULR")
    IntType(0, 4294967294)
    >>> decode_type("SLG")
    IntType(-2147483647, 2147483647)
    >>> decode_type("SLR")
    IntType(-2147483647, 2147483647)
    """
    # create missing types
    if typecode not in TYPEMAP:
        # STR       character string              Hello
        # NTS       character string              Hello
        if typecode.startswith(("STR:", "NTS:")):
            TYPEMAP[typecode] = types.StrType(_get_length(typecode))
        # HEX       hex digit string              hex octet sep by space
        if typecode.startswith("HEX:"):
            TYPEMAP[typecode] = types.HexType(_get_length(typecode))
        # BI0     bit 0                         0...1
        mat = _RE_BIT.match(typecode)
        if mat:
            TYPEMAP[typecode] = types.BoolType()
    # get type
    type_ = TYPEMAP[typecode]
    # divider
    if divider:
        type_ = type_.with_divider(divider)
    return type_


def _get_length(typecode):
    length = typecode.split(":")[1]
    if length != "*":
        return int(length)
    else:
        return None
