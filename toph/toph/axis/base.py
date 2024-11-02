"""Base Axis object"""

from abc import ABC
from typing import Any, Tuple


class BaseAxis(ABC):
    """Base axis object defines the methods
    all axes must abide
    """

    # TODO: only linear for now? But what about non-linear?
    def __init__(self, domain: Tuple[Any], range_: Tuple[Any], *args, **kwargs):
        """All Axis objects must have some domain and some range"""

    def convert(self, dp: Any) -> Any:
        """Method converts"""
        raise NotImplementedError("convert method must be implemented")

    def __call__(self, *args, **kwargs):
        """Shortcut to call the convert method"""
        return self.convert(*args, **kwargs)
