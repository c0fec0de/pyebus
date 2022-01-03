import pathlib

import pytest

from pyebus import AUTO, FieldDef, MsgDef, MsgDefs
from pyebus.msgdefdecoder import decode_msgdef
from pyebus.types import HourMinuteType, IntType, TimeType

from .util import cmp_

TESTDATAPATH = pathlib.Path(__file__).parent / "testdata"


def test_msgdefs0():
    """Message Defs."""
    msgdefs = MsgDefs()

    # load
    infilepath = TESTDATAPATH / "find0.txt"
    for line in infilepath.read_text().splitlines():
        if line:
            try:
                msgdefs.add(decode_msgdef(line))
            except ValueError as e:
                pass

    assert len(msgdefs) == 777
    assert msgdefs.summary() == "777 messages (685 read, 19 update, 231 write) with 1653 fields"

    assert msgdefs.get("bai", "foo") is None
    assert msgdefs.get("bar", "foo") is None
    assert msgdefs.get_ident("cc/StatPowerOn") == MsgDef(
        "cc", "StatPowerOn", (FieldDef(0, "", IntType(0, 65534)),), read=True
    )
    assert msgdefs.get_ident("cc/StatPowerOff") is None

    assert len(msgdefs.find("?c")) == 132
    assert list(msgdefs.find("cc", "StatPowerOn")) == [
        MsgDef("cc", "StatPowerOn", (FieldDef(0, "", IntType(0, 65534)),), read=True)
    ]

    with pytest.raises(ValueError):
        msgdefs.resolve(["a/"])
    with pytest.raises(ValueError):
        msgdefs.resolve(["a/b/c/"])
    with pytest.raises(ValueError):
        msgdefs.resolve(["/b/"])

    assert list(msgdefs.resolve(["*/FlowTempDesired/temp1", "cc/StatPowerOn", "hc/FlowTemp*"])) == [
        MsgDef(
            "hc",
            "FlowTempDesired",
            (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C", comment="Temperatur"),),
            read=True,
        ),
        MsgDef(
            "hc",
            "FlowTempMax",
            (FieldDef(0, "temp0", IntType(0, 254), unit="°C", comment="Temperatur"),),
            read=True,
            write=True,
        ),
        MsgDef(
            "hc",
            "FlowTempMin",
            (FieldDef(0, "temp0", IntType(0, 254), unit="°C", comment="Temperatur"),),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc",
            "FlowTempDesired",
            (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C", comment="Temperatur"),),
            read=True,
        ),
        MsgDef(
            "mc.3",
            "FlowTempDesired",
            (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C", comment="Temperatur"),),
            read=True,
        ),
        MsgDef(
            "mc.4",
            "FlowTempDesired",
            (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C", comment="Desired flow temperature of MK1"),),
            read=True,
        ),
        MsgDef(
            "mc.5",
            "FlowTempDesired",
            (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C", comment="Desired flow temperature of MK2"),),
            read=True,
        ),
        MsgDef("cc", "StatPowerOn", (FieldDef(0, "", IntType(0, 65534)),), read=True),
    ]

    assert list(msgdefs.resolve(["mc.5/Timer.*/foo"])) == []
    assert list(msgdefs.resolve(["mc.5/Timer.*/to*"])) == [
        MsgDef(
            "mc.5",
            "Timer.Friday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc.5",
            "Timer.Monday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc.5",
            "Timer.Saturday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc.5",
            "Timer.Sunday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc.5",
            "Timer.Thursday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc.5",
            "Timer.Tuesday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
        MsgDef(
            "mc.5",
            "Timer.Wednesday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            write=True,
        ),
    ]

    assert list(msgdefs.resolve(["mc.5/Timer.Friday#3/to*"])) == [
        MsgDef(
            "mc.5",
            "Timer.Friday",
            (
                FieldDef(1, "to.0", HourMinuteType(minres=10), comment="bis"),
                FieldDef(3, "to.1", HourMinuteType(minres=10), comment="bis"),
                FieldDef(5, "to.2", HourMinuteType(minres=10), comment="bis"),
            ),
            read=True,
            setprio=3,
            write=True,
        )
    ]


def test_msgdefs1():
    """Message Defs."""
    msgdefs = MsgDefs()

    # load
    infilepath = TESTDATAPATH / "find1.txt"
    for line in infilepath.read_text().splitlines():
        if line:
            try:
                msgdefs.add(decode_msgdef(line))
            except ValueError as e:
                pass

    assert len(msgdefs) == 413
    assert msgdefs.summary() == "413 messages (396 read, 12 update, 229 write) with 830 fields"


def test_msgdef_add_sub():
    """Add."""
    msgdefs0 = MsgDefs()
    msgdefs0.add(
        MsgDef("hc", "FlowTempDesired", (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C"),), read=True)
    )
    msgdefs0.add(
        MsgDef("hc", "FlowTempMax", (FieldDef(0, "temp0", IntType(0, 254), unit="°C"),), read=True, write=True)
    )
    msgdefs0.add(
        MsgDef("hc", "FlowTempMin", (FieldDef(0, "temp0", IntType(0, 254), unit="°C"),), read=True, write=True)
    )

    msgdefs1 = MsgDefs()
    msgdefs1.add(
        MsgDef("hc", "FlowTempMax", (FieldDef(0, "temp0", IntType(0, 254), unit="°C"),), read=True, write=True)
    )
    msgdefs1.add(
        MsgDef("hc", "FlowTempMin", (FieldDef(0, "temp0", IntType(0, 254), unit="°C"),), read=True, write=True)
    )

    msgdefs = msgdefs0 + msgdefs1
    assert list(msgdefs) == [
        MsgDef("hc", "FlowTempDesired", (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C"),), read=True),
        MsgDef("hc", "FlowTempMax", (FieldDef(0, "temp0", IntType(0, 254), unit="°C"),), read=True, write=True),
        MsgDef("hc", "FlowTempMin", (FieldDef(0, "temp0", IntType(0, 254), unit="°C"),), read=True, write=True),
    ]

    msgdefs = msgdefs0 - msgdefs1
    assert list(msgdefs) == [
        MsgDef("hc", "FlowTempDesired", (FieldDef(0, "temp1", IntType(0, 100, divider=2), unit="°C"),), read=True),
    ]


def test_msgdef_set_defaultprio():
    """Add."""
    msgdefs = MsgDefs()
    msgdefs.add(MsgDef("hc", "read", (FieldDef(0, "temp1", IntType(0, 100)),), read=True))
    msgdefs.add(MsgDef("hc", "read", (FieldDef(0, "temp1", IntType(0, 100)),), read=True))
    msgdefs.add(MsgDef("hc", "read3", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, setprio=3))
    msgdefs.add(MsgDef("hc", "write", (FieldDef(0, "temp1", IntType(0, 100)),), write=True))
    msgdefs.add(MsgDef("hc", "update", (FieldDef(0, "temp1", IntType(0, 100)),), update=True))
    msgdefs.add(MsgDef("hc", "readwrite", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, write=True))
    assert list(msgdefs) == [
        MsgDef("hc", "read", (FieldDef(0, "temp1", IntType(0, 100)),), read=True),
        MsgDef("hc", "read3", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, setprio=3),
        MsgDef("hc", "write", (FieldDef(0, "temp1", IntType(0, 100)),), write=True),
        MsgDef("hc", "update", (FieldDef(0, "temp1", IntType(0, 100)),), update=True),
        MsgDef("hc", "readwrite", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, write=True),
    ]
    assert list(msgdef.setprio for msgdef in msgdefs) == [None, 3, None, None, None]

    msgdefs.set_defaultprio(AUTO)
    assert list(msgdefs) == [
        MsgDef("hc", "read", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, setprio=1),
        MsgDef("hc", "read3", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, setprio=3),
        MsgDef("hc", "write", (FieldDef(0, "temp1", IntType(0, 100)),), write=True),
        MsgDef("hc", "update", (FieldDef(0, "temp1", IntType(0, 100)),), update=True),
        MsgDef("hc", "readwrite", (FieldDef(0, "temp1", IntType(0, 100)),), read=True, write=True, setprio=2),
    ]
    assert list(msgdef.setprio for msgdef in msgdefs) == [1, 3, None, None, 2]
