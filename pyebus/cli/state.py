"""State Command."""
from ..const import OK
from .common import create_ebus, disable_stdout_buffering


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("state", help="Show EBUSD state")
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    state = await ebus.async_get_state()
    if state != OK:
        raise Broken(state)
    print(state)


class Broken(RuntimeError):
    """Broken State"""
