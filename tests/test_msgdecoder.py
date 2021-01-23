import pathlib
import sys

from pyebus import MsgDefs, UnknownMsgError
from pyebus.msgdecoder import MsgDecoder
from pyebus.msgdefdecoder import decode_msgdef

from .util import cmp_

TESTDATAPATH = pathlib.Path(__file__).parent / "testdata"


def test_listen0a():
    """Process `listen0a.txt`."""
    _test(TESTDATAPATH / "find0.txt", TESTDATAPATH / "listen0a", 777)


def test_listen0b():
    """Process `listen0b.txt`."""
    _test(TESTDATAPATH / "find0.txt", TESTDATAPATH / "listen0b", 777)


def test_listen1a():
    """Process `listen1a.txt`."""
    _test(TESTDATAPATH / "find1.txt", TESTDATAPATH / "listen1a", 413)


def _test(deffilepath, basepath, num):
    infilepath = basepath.with_suffix(".txt")
    outfilepath = basepath.with_suffix(".decoded.gen.txt")
    reffilepath = basepath.with_suffix(".decoded.txt")

    # load definitions
    msgdefs = MsgDefs()
    for line in deffilepath.read_text().splitlines():
        if line:
            try:
                msgdefs.add(decode_msgdef(line))
            except ValueError as e:
                print(e)

    assert len(msgdefs) == num

    # decode
    decoder = MsgDecoder(msgdefs)
    with outfilepath.open("w") as outfile:
        for line in infilepath.read_text().splitlines():
            if line:
                try:
                    outfile.write(f"\n{line}\n")
                    msg = decoder.decode_line(line)
                    if msg.valid:
                        values = tuple(f"{field.fielddef.name}={field.unitvalue!r}" for field in msg.fields)
                        outfile.write(f"  {msg.msgdef.circuit} {msg.msgdef.name} {values}\n")
                    else:
                        outfile.write(f"  {msg}\n")
                except (UnknownMsgError, ValueError) as err:
                    outfile.write(f"  {err!r}\n")

    # compare
    cmp_(outfilepath, reffilepath)
