import asyncio
import copy
from unittest.mock import patch

import pytest

import pyebus

from .util import run


def test_connect():
    """Connection succeed."""
    con = pyebus.DummyConnection()

    async def test():
        assert con.is_connected() == False
        await con.async_connect()
        assert con.is_connected() == True
        await con.async_disconnect()
        assert con.is_connected() == False
        await con.async_disconnect()
        assert con.is_connected() == False

    run(test)


def test_notconnected():
    """Not Connected."""
    con = pyebus.DummyConnection()

    async def test():
        with pytest.raises(ConnectionError):
            await con.async_write("state")

    run(test)


def test_command_error():
    """CommandError."""
    con = pyebus.DummyConnection()

    async def test():
        with pytest.raises(pyebus.CommandError):
            await con.async_write("unknown")


@patch("pyebus.Ebus.Connector", pyebus.DummyConnection)
def test_nosignal():
    """No signal."""
    ebus = pyebus.Ebus()
    dummydata = ebus.connection.dummydata
    dummydata.state = "no signal"

    async def test():
        assert await ebus.async_get_state() == "no signal"
        assert not await ebus.async_is_online()

    run(test)


@patch("pyebus.Ebus.Connector", pyebus.DummyConnection)
def test_online():
    """Online."""
    ebus = pyebus.Ebus()
    dummydata = ebus.connection.dummydata

    async def test():
        assert await ebus.async_get_state() == pyebus.OK
        assert await ebus.async_is_online()
        info = dict(line.split(": ", 1) for line in dummydata.info)
        assert await ebus.async_get_info() == info

    run(test)


@patch("pyebus.Ebus.Connector", pyebus.DummyConnection)
def test_cmd():
    """Cmd."""
    ebus = pyebus.Ebus()

    dummydata = ebus.connection.dummydata

    async def test():
        lines = [line async for line in ebus.async_cmd("state")]
        assert lines == [dummydata.state]

        lines = [line async for line in ebus.async_cmd("unknown")]
        assert lines == ["ERR: command not found"]

    run(test)


@patch("pyebus.Ebus.Connector", pyebus.DummyConnection)
@patch("pyebus.const.DEFAULT_SCANINTERVAL", 0)
def test_running():
    """Running."""
    ebus = pyebus.Ebus()
    dummydata = ebus.connection.dummydata
    ebus.scaninterval = 0.1

    async def test():
        await ebus.async_wait_scancompleted()
        await ebus.async_load_msgdefs()
        assert ebus.msgdefcodes == dummydata.finddef
        assert ebus.msgdefs.summary() == "31 messages (30 read, 1 update, 2 write) with 33 fields"
        msgdefs = ebus.msgdefs
        allmsgdefs = msgdefs.resolve("*/*")

        assert ebus.circuitinfos == tuple()
        await ebus.async_load_circuitinfos()
        assert ebus.circuitinfos == (
            pyebus.CircuitInfo("bai", "Vaillant", "BAI00", "0204", "9602", 8),
            pyebus.CircuitInfo("cc", "Vaillant", "VR630", "0500", "6301", 35),
            pyebus.CircuitInfo("hc", "Vaillant", "VR630", "0500", "6301", 38),
            pyebus.CircuitInfo("hwc", "Vaillant", "VR630", "0500", "6301", 37),
            pyebus.CircuitInfo("mc", "Vaillant", "VR630", "0500", "6301", 80),
            pyebus.CircuitInfo("mc.3", "Vaillant", "VR630", "0500", "6301", 81),
            pyebus.CircuitInfo("mc.4", "Vaillant", "MC2", "0500", "6301", 82),
            pyebus.CircuitInfo("mc.5", "Vaillant", "MC2", "0500", "6301", 83),
            pyebus.CircuitInfo("rcc", "Vaillant", "RC C", "0508", "6201", 117),
            pyebus.CircuitInfo("rcc.3", "Vaillant", "RC C", "0508", "6201", 245),
            pyebus.CircuitInfo("rcc.4", "Vaillant", "RC C", "0508", "6201", 28),
            pyebus.CircuitInfo("rcc.5", "Vaillant", "RC C", "0508", "6201", 60),
            pyebus.CircuitInfo("ui", "Vaillant", "UI", "0508", "6201", 21),
        )
        assert ebus.get_circuitinfo("rcc.3") == pyebus.CircuitInfo("rcc.3", "Vaillant", "RC C", "0508", "6201", 245)
        assert ebus.get_circuitinfo("unknown") is None

        ebus.msgdefcodes = [""]
        ebus.decode_msgdefcodes()
        assert ebus.msgdefs.summary() == "0 messages (0 read, 0 update, 0 write) with 0 fields"
        assert msgdefs is ebus.msgdefs

        ebus.msgdefs = allmsgdefs
        assert ebus.msgdefs.summary() == "31 messages (30 read, 1 update, 2 write) with 33 fields"

    run(test)


@patch("pyebus.Ebus.Connector", pyebus.DummyConnection)
def test_read_write():
    """Read Write."""
    ebus = pyebus.Ebus()
    ebus.connection.data[("bai", "FlowTemp")] = "0;cutoff;0"

    async def test():
        await ebus.async_load_msgdefs()
        msgdef = ebus.msgdefs.get("bai", "FlowTemp")
        msgdef1 = tuple(ebus.msgdefs.resolve("bai/FlowTemp/sensor"))[0]
        msg = await ebus.async_read(msgdef)
        assert msg.values == (0.0, "cutoff", "cutoff")
        await ebus.async_write(msgdef1, "ok")
        msg = await ebus.async_read(msgdef, setprio=pyebus.AUTO)
        assert msg.values == (0.0, "ok", 0.0)

        assert ebus.connection.prios == {("bai", "FlowTemp"): "2"}

        msgdef = ebus.msgdefs.get("bai", "FanPWMSum")
        await ebus.async_write(msgdef, 5)

        msgdef = ebus.msgdefs.get("bai", "FanPWMTest")
        with pytest.raises(ValueError):
            await ebus.async_write(msgdef, 5)

    run(test)
