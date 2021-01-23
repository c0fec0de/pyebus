import asyncio
import collections
import filecmp
import os
import shutil

_LEARN = False


def cmp_(out, ref):
    """Compare files."""
    if _LEARN:
        shutil.copyfile(out, ref)
    else:
        assert filecmp.cmp(out, ref), out
    os.remove(out)


async def async_run(test, server=None):
    """Run `test` with `server`."""
    if server:
        await server.async_start()
        await asyncio.sleep(0.01)
        await test()
        await server.async_stop()
        await server.async_wait_closed()
    else:
        await test()


def run(test, server=None):
    """Run `test` with `server`."""
    asyncio.run(async_run(test, server=server))
