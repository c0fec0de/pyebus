"""State Command."""
from .common import create_ebus, disable_stdout_buffering


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("info", help="Show EBUSD meta information")
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    info = await ebus.async_get_info()
    for name, value in info.items():
        print(f"{name:<22s} {value}")
