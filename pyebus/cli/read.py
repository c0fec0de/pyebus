"""Read Command."""
from .common import (
    add_msgdef_args,
    add_patterns_arg,
    add_read_args,
    async_load_msgdefs,
    create_ebus,
    disable_stdout_buffering,
    print_msg,
)


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("read", help="Read values from the bus, decode and print")
    add_msgdef_args(parser)
    add_read_args(parser, ttl=0)
    add_patterns_arg(parser, opt=True)
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    await async_load_msgdefs(ebus, args)
    msgdefs = ebus.msgdefs.resolve(args.patterns, filter_=lambda msgdef: msgdef.read or msgdef.update)
    if args.defaultprio:
        msgdefs.set_defaultprio(args.defaultprio)
    print(f"Reading to {msgdefs.summary()}")
    for msgdef in msgdefs:
        if msgdef.read:
            msg = await ebus.async_read(msgdef, ttl=args.ttl)
            print_msg(msg)
