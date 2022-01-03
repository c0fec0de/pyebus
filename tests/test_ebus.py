import asyncio
import copy

import pytest

import pyebus

from .util import run

UNUSED_PORT = 4445


def test_defaults():
    """Defaults."""
    ebus = pyebus.Ebus()
    assert ebus.host == "127.0.0.1"
    assert ebus.port == 8888
    assert ebus.scaninterval == 10
    assert ebus.scans == 3
    assert ebus.ident == "127.0.0.1:8888"
    assert ebus.msgdefcodes == []
    assert repr(ebus) == "Ebus()"


def test_params():
    """Params."""
    ebus = pyebus.Ebus("host1", 4445, scaninterval=8, scans=9)
    assert ebus.host == "host1"
    assert ebus.port == 4445
    assert ebus.scaninterval == 8
    assert ebus.scans == 9
    assert ebus.ident == "host1:4445"
    assert ebus.msgdefcodes == []
    assert repr(ebus) == "Ebus(host='host1', port=4445, scaninterval=8, scans=9)"

    ebus2 = copy.copy(ebus)
    assert ebus2.host == "host1"
    assert ebus2.port == 4445
    assert ebus2.scaninterval == 8
    assert ebus2.scans == 9
    assert ebus2.ident == "host1:4445"
    assert ebus2.msgdefcodes == []


def test_offline():
    """Offline."""
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    async def test():
        assert await ebus.async_get_state() == "no ebusd connection"
        assert not await ebus.async_is_online()
        with pytest.raises(ConnectionRefusedError):
            assert await ebus.async_get_info()

    run(test)


def test_nosignal():
    """No signal."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    server.dummydata.state = "no signal"
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    async def test():
        assert await ebus.async_get_state() == "no signal"
        assert not await ebus.async_is_online()

    run(test, server=server)


def test_online():
    """Online."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    async def test():
        assert await ebus.async_get_state() == pyebus.OK
        assert await ebus.async_is_online()
        info = dict(line.split(": ", 1) for line in server.dummydata.info)
        assert await ebus.async_get_info() == info
        await ebus.connection.async_disconnect()

    run(test, server=server)


def test_cmd():
    """Cmd."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    async def test():
        assert [line async for line in ebus.async_cmd("state")] == [server.dummydata.state]

        assert [line async for line in ebus.async_cmd("unknown")] == ["ERR: command not found"]

        # Dummy-Only Command
        assert [line async for line in ebus.async_cmd("stop")] == ["stopping"]

    run(test, server=server)


def test_running():
    """Running."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT, scaninterval=0.1, scans=3)

    async def test():
        await ebus.async_wait_scancompleted()
        await ebus.async_load_msgdefs()
        assert ebus.msgdefcodes == server.dummydata.finddef
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

    run(test, server=server)


def test_read_write():
    """Read Write."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    server.data[("bai", "FlowTemp")] = "0;cutoff;0"

    async def test():
        await ebus.async_load_msgdefs()
        msgdef = ebus.msgdefs.get("bai", "FlowTemp")
        msgdef1 = tuple(ebus.msgdefs.resolve("bai/FlowTemp/sensor"))[0]
        msg = await ebus.async_read(msgdef)
        assert msg.values == (0.0, "cutoff", "cutoff")
        await ebus.async_write(msgdef1, "ok")
        msg = await ebus.async_read(msgdef, setprio=pyebus.AUTO)
        assert msg.values == (0.0, "ok", 0.0)

        assert server.prios == {("bai", "FlowTemp"): "2"}

        msgdef = ebus.msgdefs.get("bai", "FanPWMSum")
        await ebus.async_write(msgdef, 5)

        msgdef = ebus.msgdefs.get("bai", "FanPWMTest")
        with pytest.raises(ValueError):
            await ebus.async_write(msgdef, 5)

        server.notwriteable.append(("bai", "FanPWMSum"))
        msgdef = ebus.msgdefs.get("bai", "FanPWMSum")
        with pytest.raises(pyebus.CommandError):
            await ebus.async_write(msgdef, 5)

    run(test, server=server)


def test_observe():
    """Observe."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    async def test():
        await ebus.async_load_msgdefs()

        assert server.prios == {}

        msgs = []
        async for msg in ebus.async_observe(setprio=3):
            msgs.append((msg.ident, msg.values))
            if len(msgs) > 50:
                break
        assert msgs == [
            ("bai/AntiCondensValue", (0,)),
            ("bai/BlockTimeHcMax", (0,)),
            ("bai/BoilerType", (0,)),
            ("bai/ChangesDSN", (0,)),
            ("bai/CirPump", (0,)),
            ("bai/CodingResistor", (None,)),
            ("bai/CounterStartAttempts3", (0,)),
            ("bai/CounterStartAttempts4", (0,)),
            ("bai/CounterStartattempts1", (0,)),
            ("bai/CounterStartattempts2", (0,)),
            ("bai/DCRoomthermostat", (0,)),
            ("bai/DSN", (0,)),
            ("bai/DSNOffset", (0,)),
            ("bai/DSNStart", (0,)),
            ("bai/DeactivationsTemplimiter", (0,)),
            ("bai/DeltaFlowReturnMax", (0.0,)),
            ("bai/DisplayMode", (0,)),
            ("bai/EbusSourceOn", (0,)),
            ("bai/EbusVoltage", (0,)),
            ("bai/ExtFlowTempDesiredMin", (0.0,)),
            ("bai/ExtStorageModulCon", (0,)),
            ("bai/ExternGasvalve", (0,)),
            ("bai/ExternalFaultmessage", (0,)),
            ("bai/FanHours", (0,)),
            ("bai/FanPWMSum", (0,)),
            ("bai/FanPWMTest", (0,)),
            # ("bai/FlowTemp", (0.0, pyebus.NA, pyebus.NA)),
            (
                "bai/FlowTemp",
                (
                    0.0,
                    pyebus.NA,
                ),
            ),
            ("bai/averageIgnitiontime", (0.0,)),
            ("bai/dcfState", (0,)),
            ("bai/extWP", (0,)),
            ("bai/FlowTemp", (6.125, "ok", 6.125)),
            ("bai/FlowTemp", (0.125, "ok", 0.125)),
            ("bai/FlowTemp", (1.125, "ok", 1.125)),
            ("bai/FlowTemp", (2.125, "ok", 2.125)),
            ("bai/FlowTemp", (None, pyebus.NA, pyebus.NA)),
            ("bai/FlowTemp", (None, None, None)),
            ("bai/FlowTemp", (3.125, "ok", 3.125)),
        ]

        assert len(server.prios) == 30

    run(test, server=server)


def test_observe_filter():
    """Observe."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT)

    async def test():
        await ebus.async_load_msgdefs()

        msgs = []
        msgdefs = ebus.msgdefs.resolve("bai/FlowTemp")
        async for msg in ebus.async_observe(msgdefs):
            msgs.append((msg.ident, msg.values))
        assert msgs == [
            ("bai/FlowTemp", (0.0, pyebus.NA, pyebus.NA)),
            ("bai/FlowTemp", (6.125, "ok", 6.125)),
            ("bai/FlowTemp", (0.125, "ok", 0.125)),
            ("bai/FlowTemp", (1.125, "ok", 1.125)),
            ("bai/FlowTemp", (2.125, "ok", 2.125)),
            ("bai/FlowTemp", (None, pyebus.NA, pyebus.NA)),
            ("bai/FlowTemp", (None, None, None)),
            ("bai/FlowTemp", (3.125, "ok", 3.125)),
        ]

    run(test, server=server)


def test_listen_broken():
    """Listen Broken."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    ebus = pyebus.Ebus(port=UNUSED_PORT)
    server.dummydata.listen = None

    async def test():
        await ebus.async_load_msgdefs()
        with pytest.raises(pyebus.CommandError):
            async for msg in ebus.async_listen():
                pass

    run(test, server=server)
