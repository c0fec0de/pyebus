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
from .circuitmap import CircuitMap  # noqa
from .connection import CommandError  # noqa
from .connection import Connection  # noqa
from .connection import Shutdown  # noqa
from .const import AUTO  # noqa
from .const import NA  # noqa
from .const import OK  # noqa
from .dummyserver import DummyServer
from .ebus import Ebus  # noqa
from .icon import get_icon  # noqa
from .msg import BrokenMsg  # noqa
from .msg import Field  # noqa
from .msg import Msg  # noqa
from .msgdecoder import UnknownMsgError  # noqa
from .msgdef import FieldDef  # noqa
from .msgdef import MsgDef  # noqa
from .msgdef import VirtFieldDef  # noqa
from .msgdef import resolve_prio  # noqa
from .msgdefs import MsgDefs  # noqa
from .prioritizer import Prioritizer
