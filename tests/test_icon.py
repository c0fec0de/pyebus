import collections
import pathlib

from pyebus import MsgDefs, get_icon
from pyebus.msgdefdecoder import decode_msgdef

from .util import cmp_

TESTDATAPATH = pathlib.Path(__file__).parent / "testdata"


def test_msgdefs0():
    """Message Defs."""
    msgdefs = MsgDefs()

    # load
    infilepaths = (TESTDATAPATH / "find0.txt", TESTDATAPATH / "find1.txt")
    for infilepath in infilepaths:
        for line in infilepath.read_text().splitlines():
            if line:
                try:
                    msgdefs.add(decode_msgdef(line))
                except ValueError as e:
                    pass

    variants = collections.OrderedDict()
    for msgdef in msgdefs:
        for fielddef in msgdef.fields:
            k = msgdef.read or msgdef.update, msgdef.write, fielddef.type_, fielddef.unit
            if k not in variants:
                variants[k] = get_icon(fielddef, None) or ""

    outfilepath = TESTDATAPATH / "icon.gen.txt"
    reffilepath = TESTDATAPATH / "icon.txt"

    with outfilepath.open("w") as outfile:
        for k, icon in variants.items():
            outfile.write(f"{icon:20s} {k}\n")

    cmp_(outfilepath, reffilepath)
