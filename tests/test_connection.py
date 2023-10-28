"""Connection Testing."""

import pytest

import pyebus

from .util import run

UNUSED_PORT = 4445


def test_connection():
    """Connection Class Properties."""
    con = pyebus.Connection()
    assert con.host == "127.0.0.1"
    assert con.port == 8888
    assert con.autoconnect is False

    con = pyebus.Connection(host="foo", port=4444, autoconnect=True, timeout=5)
    assert con.host == "foo"
    assert con.port == 4444
    assert con.autoconnect is True

    assert repr(con), "Connection(host='foo', port=4444, autoconnect=True, timeout=5)"


def test_connect_fails():
    """Connection failed."""
    con = pyebus.Connection(port=UNUSED_PORT)

    async def test():
        assert con.is_connected() is False
        with pytest.raises(ConnectionRefusedError):
            await con.async_connect()
        assert con.is_connected() is False

    run(test)


def test_connect():
    """Connection succeed."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    con = pyebus.Connection(port=server.port, timeout=None)

    async def test():
        assert con.is_connected() is False
        await con.async_connect()
        assert con.is_connected() is True
        await con.async_disconnect()
        assert con.is_connected() is False
        await con.async_disconnect()
        assert con.is_connected() is False

    run(test, server=server)


def test_notconnected():
    """Not Connected."""
    con = pyebus.Connection(port=UNUSED_PORT)

    async def test():
        with pytest.raises(ConnectionError):
            await con.async_write("state")

    run(test)


def test_stop():
    """Stop Server."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    con = pyebus.Connection(port=server.port, autoconnect=True)

    async def test():
        await con.async_write("stop")

    run(test, server=server)


def test_command_error():
    """CommandError."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    con = pyebus.Connection(port=server.port, autoconnect=True)

    async def test():
        with pytest.raises(pyebus.CommandError):
            await con.async_write("unknown")
            await con.async_readresp()

    run(test, server=server)


def test_shutdown():
    """Shutdown."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    con = pyebus.Connection(port=server.port, autoconnect=True)

    async def test():
        with pytest.raises(pyebus.Shutdown):
            await con.async_write("dummyshutdown")
            await con.async_readresp()

    run(test, server=server)


def test_trailing():
    """trailing."""
    server = pyebus.DummyServer(port=UNUSED_PORT)
    con = pyebus.Connection(port=server.port, autoconnect=True)

    async def test():
        with pytest.raises(pyebus.CommandError):
            await con.async_write("dummytrailing")
            await con.async_readresp()

    run(test, server=server)
