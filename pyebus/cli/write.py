"""Write Command."""
from .common import add_msgdef_args, async_load_msgdefs, create_ebus, disable_stdout_buffering


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("write", help="Write value to the bus")
    add_msgdef_args(parser)
    parser.add_argument("field", help="Field (i.e. 'ui/OutsideTemp/temp')")
    parser.add_argument("value", help="Value to apply (i.e. '5'). 'NONE' is reserved for no value.")
    parser.set_defaults(main=_main)


async def _main(args):
    disable_stdout_buffering()
    ebus = create_ebus(args)
    await async_load_msgdefs(ebus, args)
    value = args.value if args.value != "NONE" else None
    for msgdef in ebus.msgdefs.resolve(args.field.split(";"), filter_=lambda msgdef: msgdef.write):
        await ebus.async_write(msgdef, value)
