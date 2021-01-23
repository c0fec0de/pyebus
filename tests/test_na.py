import asyncio

import pyebus


def test_na():
    """Not Available."""
    str(pyebus.NA) == "NA"
    repr(pyebus.NA) == "NA"


def test_na_cmp():
    """Not Available Compare."""
    assert pyebus.NA is pyebus.NA
    assert pyebus.NA == pyebus.NA
