"""Constants."""
from datetime import timedelta


class _NotAvailable:

    """Not Available."""

    def __str__(self):
        return "NA"

    def __repr__(self):
        return "NA"


OK = "ok"
AUTO = "A"
NA = _NotAvailable()

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888
DEFAULT_TIMEOUT = 10
DEFAULT_SCANINTERVAL = 10
DEFAULT_SCANS = 3
DEFAULT_PRIOTHRESHOLDS = [timedelta(hours=1), timedelta(hours=4), timedelta(days=1)]
