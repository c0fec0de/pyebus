"""List Command."""

from ..msgdefdecoder import decodetype
from .common import add_msgdef_args, add_patterns_arg, async_load_msgdefs, create_ebus, disable_stdout_buffering


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("ls", help="List all messages")
    add_msgdef_args(parser)
    add_patterns_arg(parser, opt=True)
    parser.add_argument(
        "--name-only",
        "-n",
        default=False,
        action="store_true",
        help="Just print names.",
    )
    parser.add_argument(
        "--type",
        "-t",
        help="Type to be checked, 'r' for readable, 'w' for writeable.",
    )
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    await async_load_msgdefs(ebus, args)
    type_ = _parse_type(args.type)
    msgdefs = ebus.msgdefs.resolve(args.patterns, filter_=lambda msgdef: _filter_type(msgdef, type_))
    print(f"Listing {msgdefs.summary()}")
    for msgdef in msgdefs:
        for fielddef in msgdef.children:
            details = fielddef.type_.comment
            if fielddef.comment:
                details += f" [{fielddef.comment}]"
            if args.name_only:
                print(fielddef.ident)
            else:
                print(f"{fielddef.ident:<40s} {msgdef.access} {details}")


def _parse_type(type_):
    if type_:
        read, _, write, update = decodetype(type_)
    else:
        read, write, update = None, None, None
    return read, write, update


def _filter_type(msgdef, type_):
    read, write, update = type_
    pairs = ((msgdef.read, read), (msgdef.write, write), (msgdef.update, update))
    return all([(exp is None or val == exp) for val, exp in pairs])
