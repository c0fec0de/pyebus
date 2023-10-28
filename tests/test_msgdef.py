"""Message Definitions."""
import pyebus

_TYPE = pyebus.types.StrType(length=2)


def test_msgdef0():
    """MsgDef Example 0"""
    m = pyebus.MsgDef("circuit", "name", (), True, 5, False, False)
    assert m.circuit == "circuit"
    assert m.name == "name"
    assert m.read is True
    assert m.prio == 5
    assert m.write is False
    assert m.update is False
    assert m.children == ()
    assert m.access == "r---5"
    assert m.ident == "circuit/name"
    # assert sys.getsizeof(m) == 104
    assert repr(m) == "MsgDef('circuit', 'name', (), read=True, prio=5)"


def test_msgdef1():
    """MsgDef Example 1"""
    m = pyebus.MsgDef("circuit", "name", (), False, None, True, False)
    assert m.circuit == "circuit"
    assert m.name == "name"
    assert m.read is False
    assert m.prio is None
    assert m.write is True
    assert m.update is False
    assert m.children == ()
    assert m.access == "-w---"
    assert m.ident == "circuit/name"
    # assert sys.getsizeof(m) == 104
    assert repr(m) == "MsgDef('circuit', 'name', (), write=True)"


def test_msgdef2():
    """MsgDef Example 2"""
    m = pyebus.MsgDef("circuit", "name", (), False, None, False, True)
    assert m.circuit == "circuit"
    assert m.name == "name"
    assert m.read is False
    assert m.prio is None
    assert m.write is False
    assert m.update is True
    assert m.children == ()
    assert m.access == "--u--"
    assert m.ident == "circuit/name"
    # assert sys.getsizeof(m) == 104
    assert repr(m) == "MsgDef('circuit', 'name', (), update=True)"


def test_fielddef0():
    """FieldDef Example 0."""
    f = pyebus.FieldDef(0, "name", _TYPE, "unit")
    pyebus.MsgDef("circuit", "name", (f,), False, None, False, True)

    assert f.name == "name"
    assert f.type_ == _TYPE
    assert f.unit == "unit"
    assert f.ident == "circuit/name/name"
    # assert sys.getsizeof(f) == 88
    assert repr(f) == "FieldDef(0, 'name', StrType(length=2), unit='unit')"


def test_eq():
    """Test EQ."""
    f0 = pyebus.FieldDef(0, "name", _TYPE, "unit")
    f1 = pyebus.FieldDef(0, "name", _TYPE, "unit")
    g1 = pyebus.FieldDef(1, "name", _TYPE, "unit")
    assert f0 == f1

    m0 = pyebus.MsgDef("circuit", "name", (f0,), False, None, False, True)
    m1 = pyebus.MsgDef("circuit", "name", (f1,), False, None, False, True)
    n1 = pyebus.MsgDef("circuit", "name", (g1,), True, None, False, True)
    assert bool(m0 == m1)
    assert not bool(m0 == n1)
    assert not bool(m0 is None)

    assert hash(m0) == hash(m1)
    assert hash(m0) != hash(n1)


def test_hash():
    """Test Hash."""
    f0 = pyebus.FieldDef(0, "name", _TYPE, "unit")
    f1 = pyebus.FieldDef(0, "name", _TYPE, "unit")
    assert hash(f0) == hash(f1)
