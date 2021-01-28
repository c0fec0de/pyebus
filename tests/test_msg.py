import sys

import pyebus


def test_msgdef0():
    """MsgDef Example 0"""
    fielddef = pyebus.FieldDef(0, "uname", "name", pyebus.types.Type(), "unit")
    msgdef = pyebus.MsgDef("circuit", "name", (fielddef,), True, 5, False, False)

    fields = (pyebus.Field(fielddef, "5"),)
    msg = pyebus.Msg(msgdef, fields)

    assert repr(msg) == "Msg('circuit/name', (Field('uname', '5'),))"
    assert repr(fields[0]) == "Field('uname', '5')"

    assert msg.ident == "circuit/name"
    assert fields[0].ident == "circuit/name/uname"


def test_filter_msg():
    """Message Filtering."""
    fielddef0 = pyebus.FieldDef(0, "uname.0", "name", pyebus.types.Type(), "unit")
    fielddef1 = pyebus.FieldDef(0, "uname.1", "name", pyebus.types.Type(), "unit")
    fielddef0_ = pyebus.FieldDef(0, "uname.0", "name", pyebus.types.Type(), "unit")
    fielddef5 = pyebus.FieldDef(0, "uname", "name", pyebus.types.Type(), "unit")
    msgdef01 = pyebus.MsgDef("circuit0", "name", (fielddef0, fielddef1), True, 5, False, False)
    msgdef0 = pyebus.MsgDef("circuit0", "name", (fielddef0_,), True, 5, False, False)
    msgdef5 = pyebus.MsgDef("circuit5", "name", (fielddef5,), True, 5, False, False)

    field0 = pyebus.Field(fielddef0, "4")
    field1 = pyebus.Field(fielddef1, "5")
    field0_ = pyebus.Field(fielddef0_, "4")
    field5 = pyebus.Field(fielddef5, "5")
    msg01 = pyebus.Msg(msgdef01, (field0, field1))
    msg0 = pyebus.Msg(msgdef0, (field0_,))
    msg5 = pyebus.Msg(msgdef5, (field5,))

    b = pyebus.BrokenMsg(msgdef0, "error")

    assert pyebus.msg.filter_msg(msg5, [msgdef01]) is None  # not in
    assert pyebus.msg.filter_msg(msg01, [msgdef5, msgdef01]) == msg01  # in
    assert pyebus.msg.filter_msg(msg01, [msgdef5, msgdef0]) == msg0  # strip
    assert pyebus.msg.filter_msg(b, [msgdef0]) is b
    assert pyebus.msg.filter_msg(b) is b
    assert pyebus.msg.filter_msg(None) is None

    assert msg01.values == ("4", "5")
    assert msg0.values == ("4",)
    assert msg5.values == ("5",)
    assert b.values == tuple()
