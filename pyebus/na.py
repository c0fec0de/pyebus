"""Not Available."""


class NotAvailable:

    """Not Available Singleton."""

    __instance = None

    def __new__(cls):
        if NotAvailable.__instance is None:
            NotAvailable.__instance = object.__new__(cls)
        return NotAvailable.__instance

    def __str__(self):
        return "Not Available"

    def __repr__(self):
        return "NA"


NA = NotAvailable()
