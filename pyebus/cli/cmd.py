"""Generic Command."""

from .common import create_ebus


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser(
        "cmd",
        help=(
            "Issue TCP Command on EBUSD. "
            "See https://github.com/john30/ebusd/wiki/3.1.-TCP-client-commands for reference."
        ),
    )
    parser.add_argument(
        "--infinite", "-i", default=False, action="store_true", help="Do not abort command processing on empty line."
    )

    parser.add_argument(
        "cmd",
        help=("TCP Command. " "See https://github.com/john30/ebusd/wiki/3.1.-TCP-client-commands for reference."),
    )
    parser.set_defaults(main=_main)


async def _main(args):
    ebus = create_ebus(args)
    async for line in ebus.async_cmd(args.cmd, infinite=args.infinite, check=not args.infinite):
        print(line)
