import pathlib

from pyebus import util
from pyebus.msgdefdecoder import decode_msgdef

from .util import cmp_

TESTDATAPATH = pathlib.Path(__file__).parent / "testdata"


def test_find0():
    """Process `find0.txt`."""
    _test(TESTDATAPATH / "find0")


def test_find1():
    """Process `find1.txt`."""
    _test(TESTDATAPATH / "find1")


def _test(basepath):
    infilepath = basepath.with_suffix(".txt")
    outfilepath = basepath.with_suffix(".decoded.gen.txt")
    reffilepath = basepath.with_suffix(".decoded.txt")
    with outfilepath.open("w") as outfile:
        for line in infilepath.read_text().splitlines():
            if line:
                try:
                    msgdef = decode_msgdef(line)
                    msgdefrepr = util.repr_(
                        msgdef,
                        (msgdef.circuit, msgdef.name),
                        [
                            ("read", msgdef.read, False),
                            ("prio", msgdef.prio, None),
                            ("write", msgdef.write, False),
                            ("update", msgdef.update, False),
                        ],
                    )
                    outfile.write(f"\n{line}\n{msgdefrepr}\n")
                    for field in msgdef.children:
                        outfile.write(f"    {field!r}\n")
                except ValueError as e:
                    outfile.write(f"{e}\n")
    cmp_(outfilepath, reffilepath)
