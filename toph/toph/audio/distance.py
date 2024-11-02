"""Distance Models for Spatial Audio"""

from abc import ABC


class BaseDistanceModel(ABC):
    """Base distance model class"""

    def power_loss(self, r: float) -> float:
        """Should return a coefficient
        consistent with the power loss due
        to audio source being played at a distance
        :param r:
        :type r: float
        :returns: loss coefficient
        :rtype: float
        """
        raise NotImplementedError(
            "power_loss method must be implemented for a distance model"
        )

    def __call__(self, *args, **kwargs) -> float:
        """Just a shortcut to the power_loss method"""
        return self.power_loss(*args, **kwargs)


class IPLDistanceModel(BaseDistanceModel):
    """An implementation of the Inverse power-law distance
    model
    """

    def __init__(self, a: float = 1.0, p: float = 2.0):
        """Initialize IPL with the given hyper-parameters
        :param a: the multiplicative constant a * (vol)**(-p)
        :type a: float
        :param p: the power constant
        :type p: float
        """
        self.a: float = a
        self.p: float = p

    def power_loss(self, r: float) -> float:
        """Should return a coefficient
        consistent with the power loss due
        to audio source being played at a distance
        :param r:
        :type r: float
        :returns: loss coefficient
        :rtype: float
        """
        return self.a * (1 / r) ** self.p
