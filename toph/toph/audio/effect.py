"""Basic Effects"""

from abc import ABC

import numpy as np


class Effect(ABC):
    """All effects must inherit this
    abstract class
    """

    def apply(self, data: np.ndarray) -> np.ndarray:
        """All effects must implement this"""
        raise NotImplementedError("All effects must implement this")


class SimplePanner(Effect):
    """The simplest spatial panner (l/r)"""

    def __init__(self, dir: float = 0):
        """
        :param dir: direction of the sound [-1, 1]
        :type dir: float
        """
        self.dir: float = dir

    def apply(self, data: np.ndarray) -> np.ndarray:
        """Apply directionality"""

        ndata = np.empty((data.shape[0],))

        real_dir = (self.dir + 1) / 2
        ndata[0::2] = data[0::2] * (1.0 - real_dir)
        ndata[1::2] = data[1::2] * real_dir

        return ndata
