"""
Pythonic Interface to EBUS Daemon (EBUSD_).

Overview
========

* :any:`Ebus`: the EBUS handle, using one :any:`Connection` to an EBUSD instance.
  One EBUSD server can handle multiple :any:`Ebus` instances.
* :any:`MsgDef`: Message Definition containing multiple Field Defintions :any:`FieldDef`.
  A Virtual Field Definition :any:`VirtFieldDef` is a calculated value based on other fields.
* :any:`MsgDefs`: is a container for message definitions (:any:`MsgDef`).
* :any:`types`: contains the type engine, which allows the simple decode and
  encode of EBUSD values to/from python values.
* :any:`DummyConnection` emulates a connection. It answers requests by delegating to :any:`Dummy`.
* :any:`DummyServer` emulates an entire EBUS-daemon by delegating to :any:`Dummy`.
* :any:`Dummy` with :any:`DummyData` which emulates a minimal set of EBUS functions, for basic testing and trials.

All other classes and methods are just helper.

.. _EBUSD: https://github.com/john30/ebusd
"""
try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

from . import types
from .circuitinfo import CircuitInfo
from .circuitmap import CircuitMap
from .connection import CommandError, Connection, Shutdown
from .const import AUTO, NA, OK
from .dummyconnection import DummyConnection
from .dummydata import DummyData
from .dummyserver import DummyServer
from .ebus import Ebus
from .exceptions import UnknownMsgError
from .icon import get_icon
from .msg import BrokenMsg, Field, Msg
from .msgdef import FieldDef, MsgDef, VirtFieldDef, resolve_prio
from .msgdefs import MsgDefs
from .prioritizer import Prioritizer
