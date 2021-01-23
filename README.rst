.. image:: https://badge.fury.io/py/pyebus.svg
    :target: https://badge.fury.io/py/pyebus

.. image:: https://img.shields.io/pypi/dm/pyebus.svg?label=pypi%20downloads
   :target: https://pypi.python.org/pypi/pyebus

.. image:: https://travis-ci.org/c0fec0de/pyebus.svg?branch=main
    :target: https://travis-ci.org/c0fec0de/pyebus

.. image:: https://readthedocs.org/projects/pyebus/badge/?version=latest
    :target: https://pyebus.readthedocs.io/en/latest/?badge=latest

.. image:: https://codeclimate.com/github/c0fec0de/pyebus.png
    :target: https://codeclimate.com/github/c0fec0de/pyebus

.. image:: https://img.shields.io/pypi/pyversions/pyebus.svg
   :target: https://pypi.python.org/pypi/pyebus

.. image:: https://img.shields.io/badge/code%20style-pep8-brightgreen.svg
   :target: https://www.python.org/dev/peps/pep-0008/

.. image:: https://img.shields.io/badge/code%20style-pep257-brightgreen.svg
   :target: https://www.python.org/dev/peps/pep-0257/

Pythonic interface to EBUSD_.


Installation
============

To install the `pyebus` module run::

    pip install pyebus

If you do not have write-permissions to the python installation, try::

    pip install pyebus --user

Command-Line-Interface
======================

Usage::

	usage: ebustool [-h] [--host HOST] [--port PORT] [--timeout TIMEOUT] [--version] [--debug] {cmd,listen,ls,observe,read,state,write,info} ...

	positional arguments:
	  {cmd,listen,ls,observe,read,state,write,info}
	                        Sub Commands
	    cmd                 Issue TCP Command on EBUSD. See https://github.com/john30/ebusd/wiki/3.1.-TCP-client-commands for reference.
	    listen              Listen on the bus, decode messages and and print
	    ls                  List all messages
	    observe             Read all known messages once and continue listening so that ALL EBUS values are available, decode every message and print.
	    read                Read values from the bus, decode and print
	    state               Show EBUSD state
	    write               Write value to the bus
	    info                Show EBUSD meta information

	optional arguments:
	  -h, --help            show this help message and exit
	  --host HOST, -H HOST  EBUSD address. Default is '127.0.0.1'.
	  --port PORT, -P PORT  EBUSD port. Default is 8888.
	  --timeout TIMEOUT, -T TIMEOUT
	                        EBUSD connection timeout. Default is 10.
	  --version             show program's version number and exit
	  --debug

List all messages and fields
----------------------------

The `ls` command lists all messages `CIRCUIT/MESSAGENAME/FIELDNAME     rwuSP INFO`::

	$ ebt -H 192.168.1.4 ls
	mc/DateTime/dcfstate                     r---1 nosignal, ok, sync, valid [DCF Empfängerstatus]
	mc/DateTime/btime                        r---1 HOUR:MINUTE:SECOND [Uhrzeit]
	mc/DateTime/bdate                        r---1 DAY.MONTH.YEAR [Datum]
	mc/DateTime/temp2                        r---1 Float within [-127.99:127.99] with 0.00390625 fraction
	mc/DateTime/bdate+btime+dcfstate         r---1 DAY.MONTH.YEAR HOUR:MINUTE:SECOND
	mc/FlowTemp/temp                         r---1 Float within [-2047.9:2047.9] with 0.0625 fraction [Temperatur]
	mc/FlowTemp/sensor                       r---1 ok, circuit, cutoff
	mc/FlowTemp/temp+sensor                  r---1 Float within [-2047.9:2047.9] with 0.0625 fraction
	mc/FlowTempDesired/temp1                 r---1 Float within [0:100] with 0.5 fraction
	mc/FlowTempMax/temp0                     rw--2 Integer within [0:254]
	mc/FlowTempMin/temp0                     rw--2 Integer within [0:254]
	mc/OperatingMode/mcmode                  rw--2 disabled, on, off, auto, eco, low
	mc/TempDesired/temp1                     rw--2 Float within [0:100] with 0.5 fraction
	mc/TempDesiredLow/temp1                  rw--2 Float within [0:100] with 0.5 fraction

`CIRCUIT/MESSAGENAME/FIELDNAME` is a unique message field identifier.
`CIRCUIT` names the device which contains the information.
`MESSAGENAME` is the name of the message on the bus.
Each message consists of fields.
`FIELDNAME` identifies the specific information within the message.
EBUSD fieldnames are **NOT** unique. `pyebus` appends a suffix in case of naming collisions.
Field names with a `+` are virtual and just the concatenation of existing fields.

The access rights have the following meaning:

* `r`: The message is explicitly readable.
* `w`: The message is explicitly writable.
* `u`: The message is **NOT** readable, but emitted by the sender on change.
* `S`: Is the poll priority to be set. **This applies to readable messages only.** Values `1-9` can be used. `A` is a placeholder for automatic. This will choose an appropriate priority.
* `P`: Actual polling priority.

List some messages and fields
-----------------------------

The `ls` command accepts explicit names with wildcards and placeholders. **Case-Insensitive**.

	$ ebt -H 192.168.1.4 ls "mc/FlowTemp*"
	mc/FlowTemp/temp                         r---1 Float within [-2047.9:2047.9] with 0.0625 fraction [Temperatur]
	mc/FlowTemp/sensor                       r---1 ok, circuit, cutoff
	mc/FlowTemp/temp+sensor                  r---1 Float within [-2047.9:2047.9] with 0.0625 fraction
	mc/FlowTempDesired/temp1                 r---1 Float within [0:100] with 0.5 fraction
	mc/FlowTempMax/temp0                     rw--2 Integer within [0:254]
	mc/FlowTempMin/temp0                     rw--2 Integer within [0:254]

	$ ebt -H 192.168.1.4 ls "*/*mode*"
	mc/OperatingMode/mcmode                  rw--2 disabled, on, off, auto, eco, low

Read messages and fields
------------------------

`read` behaves identical to `ls` (with or without patterns), but returns the actual value::

	$ ebt -H 192.168.1.4 read "*/*mode*"
	mc/OperatingMode/mcmode                  rw--2 eco                 disabled, on, off, auto, eco, low

Non-readable messages are filtered automatically.

Please note, EBUS is slow. EBUSD only reads values which are older than 300s or not cached.
`--ttl` explicitly specifies the maximum age in seconds.

Write Message Field
-------------------

Each writable field can be set by::

	$ ebt -H 192.168.1.4 write mc/OperatingMode/mcmode auto

EBUS Status
-----------

The EBUS status can be retrieved by::

	$ ebt -H 192.168.1.4 state
	ok

or more detailled::

	$ ebt -H 192.168.1.4 info
	version                ebusd 21.1.v21.1-12-gccfc025
	update check           version 3.4 available
	signal                 acquired
	symbol rate            114
	max symbol rate        217
	min arbitration micros 317
	max arbitration micros 4751
	min symbol latency     0
	max symbol latency     10
	reconnects             0
	masters                7
	messages               1006
	conditional            14
	poll                   597
	update                 10
	address 03             master #11
	address 08             slave #11, scanned "MF=Vaillant;ID=BAI00;SW=0204;HW=9602", loaded "vaillant/bai.0010015600.inc" ([HW=9602]), "vaillant/08.bai.csv"
	address 10             master #2
	address 15             slave #2, scanned "MF=Vaillant;ID=UI   ;SW=0508;HW=6201", loaded "vaillant/15.ui.csv"
	address 17             master #17



Programming API
===============

Complete API-Documentation_

Overview
--------

`Ebus` represents one connection to a EBUSD instance.

>>> from pyebus import Ebus
>>> ebus = Ebus('127.0.0.1')

The instance needs to know the messages definitions handled by the EBUSD instance.
The EBUSD message definitions are based on a EBUSD scan algorithm and the EBUSD-configuration_.

Wait for the EBUSD scan to be completed:

>>> await ebus.async_wait_scancompleted()

Now, we can load the message definition codes and convert them to message definitions `MsgDef`.

>>> await ebus.async_load_msgdefs()

The message definitions are stored in a `MsgDefs` instance at

>>> ebus.msgdefs

A single message can be read via:

>>> msgdef = ebus.msgdefs.get('circuit', 'name')
>>> print(await ebus.async_read(msgdef))

All messages can be read via:

>>> for msgdef in ebus.msgdefs:
>>>   if msgdef.read:
>>>     print(await ebus.async_read(msgdef))

Message can be filtered via patterns `CIRCUIT/MESSAGENAME` or `CIRCUIT/MESSAGENAME/FIELDNAME`.
Wildcards (`*`) and Placeholder (`?`) are supported.
The following example will read all temperature fields and all message of the circuit named `mc`.
The read value must not be older than 1000s.

>>> for msgdef in ebus.msgdefs.resolve(['*/*/*temp*', 'mc/*']):
>>>   if msgdef.read:
>>>     print(await ebus.async_read(msgdef, ttl=1000))

Writing is also possible

>>> await ebus.async_write(msgdef, value)

EBUS meta informations are available at:

>>> await ebus.async_get_state()
>>> await ebus.async_get_info()

.. _EBUSD: https://github.com/john30/ebusd
.. _EBUSD-Configuration: https://github.com/john30/ebusd-configuration
.. _API-Documentation: https://pyebus.readthedocs.io/en/latest/api/pyebus.html
