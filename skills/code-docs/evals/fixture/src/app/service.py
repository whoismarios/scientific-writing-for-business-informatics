"""Order service used by the fixture."""

from typing import Iterator


def total(prices: list[float], discount: float = 0.0) -> float:
    """Adds up prices and applies a discount.

    Args:
        prices: Item prices in euros.
        discount: Share between 0 and 1 taken off the sum.

    Returns:
        The discounted sum.
    """
    return sum(prices) * (1 - discount)


def undocumented(order_id: int) -> dict:  # expect: DOC-MISSING
    return {"id": order_id}


def summary_only(order_id: int) -> str:  # expect-full: DOC-ARGS-MISSING, DOC-RETURNS-MISSING
    """Formats an order reference."""
    return f"ORD-{order_id}"


def multi_line(order_id: int) -> str:  # expect: DOC-ARGS-MISSING, DOC-RETURNS-MISSING
    """Formats an order reference for invoices.

    The prefix differs from the one used in e-mails.
    """
    return f"INV-{order_id}"


def stale(order_id: int, user: str) -> None:  # expect: DOC-PARAM-MISSING, DOC-PARAM-STALE
    """Cancels an order.

    Args:
        order_id: Order to cancel.
        reason: Free-text reason.
    """


def returns_in_summary(order_id: int) -> str:
    """Returns the public URL of an order.

    Args:
        order_id: Order to link.
    """
    return f"/orders/{order_id}"


def lines(path: str) -> Iterator[str]:  # expect: DOC-RETURNS-MISSING
    """Reads a file lazily.

    Args:
        path: File to read.
    """
    with open(path, encoding="utf-8") as fh:
        yield from fh


def _helper(x):
    return x


class Repository:  # expect: DOC-MISSING
    def find(self, order_id: int) -> dict:  # expect: DOC-MISSING
        return {}

    @property
    def size(self) -> int:
        """Number of stored orders."""
        return 0

    def _cache(self):
        return None

    def __len__(self):
        return 0


class Order:
    """A single order.

    Attributes:
        id: Order number.
    """

    def __init__(self, order_id: int):
        self.id = order_id

    def label(self, *args, prefix: str = "", **kwargs) -> str:
        """Builds a display label.

        Args:
            *args: Extra parts appended to the label.
            prefix: Text placed in front.
            **kwargs: Ignored.

        Returns:
            The label.
        """
        return prefix + str(self.id)
