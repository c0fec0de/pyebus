"""Command Line. Interface."""
import argparse
import asyncio
import inspect
import logging
import sys
import os

from .. import __version__
from . import cmd, dummyserver, info, listen, ls, observe, read, state, write

#: environment key for defining default value for ebusd host
ENV_KEY_EBUSD_HOST = "EBUSD_HOST"

#: environment key for defining default value for ebusd port
ENV_KEY_EBUSD_PORT = "EBUSD_PORT"


def argvhandler(argv):
    """Command Line Interface."""
    parser = argparse.ArgumentParser(prog="ebustool")

    default_ebusd_host = "127.0.0.1"
    default_ebusd_port = 8888

    try:
        default_ebusd_host = os.environ[ENV_KEY_EBUSD_HOST]
    except KeyError:
        pass
    except Exception:
        pass

    try:
        default_ebusd_port = int(os.environ[ENV_KEY_EBUSD_PORT])
    except KeyError:
        pass
    except Exception:
        print(f"Ignoring invalid port in environment variable {ENV_KEY_EBUSD_PORT}")

    parser.add_argument("--host", "-H", default=default_ebusd_host, help="EBUSD address. Default is '%(default)s'.")
    parser.add_argument(
        "--port", "-P", default=default_ebusd_port, type=int, help="EBUSD port. Default is %(default)s."
    )
    parser.add_argument("--timeout", "-T", default=10, type=int, help="EBUSD connection timeout. Default is 10.")

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.set_defaults(main=lambda args: _print_help(parser))

    # Sub Commands
    subparsers = parser.add_subparsers(help="Sub Commands")
    cmd.parse_args(subparsers)
    listen.parse_args(subparsers)
    ls.parse_args(subparsers)
    observe.parse_args(subparsers)
    read.parse_args(subparsers)
    state.parse_args(subparsers)
    write.parse_args(subparsers)
    info.parse_args(subparsers)
    dummyserver.parse_args(subparsers)

    args = parser.parse_args(argv)
    loglevel = logging.DEBUG if args.debug else logging.WARN
    logging.basicConfig(format="%(levelname)10s %(name)20s %(message)s", level=loglevel)
    if inspect.iscoroutinefunction(args.main):
        asyncio.run(args.main(args))
    else:
        args.main(args)


def _print_help(parser):
    parser.print_help()
    sys.exit(2)


def main():  # pragma: no cover
    """Command Line Hookup."""
    args = sys.argv[1:]
    if "--debug" in args:
        argvhandler(args)
    else:
        try:
            argvhandler(args)
        except Exception as exc:  # pylint: disable=W0703
            print(f"ERROR: {exc}")
            sys.exit(1)
