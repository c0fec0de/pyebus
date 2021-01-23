"""Listen Command."""

from .common import (
    add_msgdef_args,
    add_patterns_arg,
    async_load_msgdefs,
    create_ebus,
    disable_stdout_buffering,
    print_msg,
)


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("listen", help="Listen on the bus, decode messages and and print")
    add_msgdef_args(parser)
    add_patterns_arg(parser, opt=True)
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    await async_load_msgdefs(ebus, args)
    msgdefs = ebus.msgdefs.resolve(args.patterns)
    print(f"Listening to {msgdefs.summary()}")
    if msgdefs:
        async for msg in ebus.async_listen(msgdefs=msgdefs):
            print_msg(msg)
