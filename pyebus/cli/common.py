"""Common."""
import logging
import sys

import pyebus

_LOGGER = logging.getLogger(__name__).parent


def add_msgdef_args(parser):
    """Load arguments related to :any:`load_msgdef`."""
    parser.add_argument(
        "--scanwait",
        "-w",
        default=False,
        action="store_true",
        help=(
            "EBUSD scans the bus for available devices. "
            "Wait until this scan does not find any new messages. "
            "Specify this option, if EBUSD was started within the last minutes."
        ),
    )


def add_read_args(parser, ttl=None):
    """Read Arguments."""
    parser.add_argument("--defaultprio", "-p", default=None, help="Default priorty. 1-9 or A for AUTOMATIC.")
    parser.add_argument("--ttl", "-t", default=ttl, type=int, help="Maximum age of value in seconds.")


def add_patterns_arg(parser, opt=False):
    """Add patterns option."""
    if not opt:
        parser.add_argument("patterns", help="Message patterns separated by ';' (i.e. 'ui/OutsideTemp')")
    else:
        parser.add_argument(
            "patterns",
            nargs="?",
            default="*/*",
            help="Message patterns separated by ';' (i.e. 'ui/OutsideTemp'). Default is '*/*' for all.",
        )


def disable_stdout_buffering():
    """Disable STDOUT buffering."""
    sys.stdout = UnbufferedStream(sys.stdout)


def create_ebus(args):
    """Create :any:`Ebus` instance with parameters from `args`."""
    return pyebus.Ebus(host=args.host, port=args.port, timeout=args.timeout)


async def async_load_msgdefs(ebus, args):
    """Load Message Definitions."""
    if args.scanwait:
        print("Waiting for EBUSD scan to complete ... ", end="")
        await ebus.async_wait_scancompleted()
        print("DONE.")

    print("Loading Message Definitions ... ", end="")
    await ebus.async_load_msgdefs()
    print(f"{ebus.msgdefs.summary()} DONE.")


def print_msg(msg, skipbroken=False):
    """Formatted output."""
    if msg.valid:
        for field in msg.fields:
            # if isinstance(field.value, (ValueError))
            details = []
            fieldcomment = field.fielddef.comment
            if fieldcomment:
                details.append(f"({fieldcomment})")
            typecomment = field.fielddef.type_.comment
            if typecomment:
                details.append(f"{typecomment}")
            details = " ".join(details)
            unitvalue = field.unitvalue
            if unitvalue is None:
                unitvalue = ""
            print(f"{field.ident:<40s} {field.fielddef.msgdef.access} {unitvalue!s:<20s}{details}")
    elif not skipbroken:
        _LOGGER.error(f"{msg.msgdef.ident}: {msg.error}")


class UnbufferedStream:

    """Unbuffered `stream`."""

    def __init__(self, stream):
        self.stream = stream

    def write(self, *args, **kwargs):
        """Write."""
        self.stream.write(*args, **kwargs)
        self.stream.flush()

    def writelines(self, *args, **kwargs):
        """Write multiple lines."""
        self.stream.writelines(*args, **kwargs)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
