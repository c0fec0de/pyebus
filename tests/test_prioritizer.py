from datetime import timedelta
from time import sleep

from pyebus import Field, FieldDef, Msg, MsgDef, Prioritizer, types


def _init():
    fd0 = FieldDef(0, "temp", types.IntType(-127, 128))
    fd1 = FieldDef(1, "name", types.StrType(10))
    md = MsgDef("circuit", "name", [fd0, fd1], read=True)
    m0 = Msg(md, [Field(fd0, 3), Field(fd1, "foo")])
    m1 = Msg(md, [Field(fd0, 3), Field(fd1, "bar")])

    return Prioritizer((0.01, 0.03), intervals=1), md, m0, m1


def _step(p, md, m, slp, prio):
    p.notify(m)
    sleep(slp)
    assert p.get_prio(md) == prio


def test_basic():
    p = Prioritizer((0.01, 0.03))
    assert p.thresholds == (timedelta(microseconds=10000), timedelta(microseconds=30000))
    assert p.intervals == 3


def test_inc():
    """Straight increment."""
    p, md, m0, m1 = _init()
    for m in [m0] * 2 * 2:
        _step(p, md, m, 0.005, 1)
    for m in [m0] * 2 * 6:
        _step(p, md, m, 0.005, 2)
    for m in [m0] * 30:
        _step(p, md, m, 0.005, 3)

    assert tuple(p.iter_priochanges()) == ((md.ident, 3),)


def test_inc_mid():
    """Straight increment to middle."""
    p, md, m0, m1 = _init()
    for m in [m0, m1]:
        _step(p, md, m, 0.02, 1)
    for m in [m0, m1] * 10:
        _step(p, md, m, 0.02, 2)


def test_dec():
    """Straight decrement."""
    p, md, m0, m1 = _init()
    p.set_prio(md, 3)
    for m in [m0, m1]:
        _step(p, md, m, 0.005, 3)
    for m in [m0, m1]:
        _step(p, md, m, 0.005, 2)
    for m in [m0, m1] * 10:
        _step(p, md, m, 0.005, 1)


def test_dec_mid():
    """Straight decrement to middle."""
    p, md, m0, m1 = _init()
    p.set_prio(md, 3)
    for m in [m0, m1]:
        _step(p, md, m, 0.02, 3)
    for m in [m0, m1] * 10:
        _step(p, md, m, 0.02, 2)


def test_default_prio():
    p, md, m0, m1 = _init()
    assert p.get_prio(md) == 1


def test_write_prio():
    p = Prioritizer((timedelta(seconds=0.03),))
    assert p.thresholds == (timedelta(seconds=0.03),)
    md = MsgDef("circuit", "name", [], write=True)
    m = Msg(md, [])
    assert p.get_prio(md) is None
    p.notify(m)
    assert p.get_prio(md) is None
    p.set_prio(md, 2)
    assert p.get_prio(md) is None
