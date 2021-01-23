"""Write Command."""
from pyebus import DummyServer


def parse_args(subparsers):
    """Parse Arguments."""
    parser = subparsers.add_parser("dummyserver", help="Run Dummy Server, which behaves like EBUSD")
    parser.add_argument("--port", type=int, help="Listen on Port", default=8888)
    parser.set_defaults(main=_main)


async def _main(args):
    server = DummyServer(port=args.port)
    await server.async_start()
    await server.async_wait_closed()
