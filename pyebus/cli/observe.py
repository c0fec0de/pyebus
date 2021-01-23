"""Observe."""
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
    parser = subparsers.add_parser(
        "observe",
        help=(
            "Read all known messages once and continue listening so that ALL EBUS values are available, "
            "decode every message and print."
        ),
    )
    add_msgdef_args(parser)
    add_read_args(parser, ttl=10000)
    add_patterns_arg(parser, opt=True)
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    await async_load_msgdefs(ebus, args)
    msgdefs = ebus.msgdefs.resolve(args.patterns)
    if args.defaultprio:
        msgdefs.set_defaultprio(args.defaultprio)
    print(f"Observing {msgdefs.summary()}")
    async for msg in ebus.async_observe(msgdefs=msgdefs, ttl=args.ttl):
        print_msg(msg)
