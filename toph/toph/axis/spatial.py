"""Axes for projecting cartesian coordinates
into polar coordinates
"""

from typing import Tuple

import numpy as np

from toph.axis.base import BaseAxis

# TODO: python 3.12< doesn't support type syntax
Cartesian = Tuple[float, float]
Polar = Tuple[float, float, float]
SpatialRange = Tuple[Tuple[float, float], Tuple[float, float]]


class LinearSpatialAxis(BaseAxis):
    """SpatialAxis converts cartesian coordinates
    into polar coordinates (r, theta, phi)

    This is achieved by projecting the points on to an imaginary
    plane that sits directly in front of the listener at all times.

    The plane is assumed to be at unit distance, any further distance effects
    can be applied later by scaling the r in polar coordinates
    """

    def __init__(
        self,
        domain: SpatialRange,
        range_: SpatialRange,
    ):
        """
        :param domain: two tuples of range in horizontal and
        vertical dimensions, in cartesian coords
        :type domain: SpatialRange
        :param range: two tuples of range in horizontal and
        vertical dimensions, in degrees
        :type range: SpatialRange
        """
        super().__init__(domain, range_)

        # derive useful values for later
        self._do_x_range: float = max(domain[0]) - min(domain[0])
        self._do_y_range: float = max(domain[1]) - min(domain[1])
        self._do_ox: float = min(domain[0]) + self._do_x_range / 2.0
        self._do_oy: float = min(domain[1]) + self._do_y_range / 2.0

        # useful for range (this is in angles)
        self._ra_x_range: float = max(range_[0]) - min(range_[0])
        self._ra_y_range: float = max(range_[1]) - min(range_[1])
        self._ra_ox: float = min(range_[0]) + self._ra_x_range / 2.0
        self._ra_oy: float = min(range_[1]) + self._ra_y_range / 2.0

        # actual min / max (limits) in cart. coords.
        self._ra_x_lim: float = np.tan(np.radians(self._ra_x_range / 2.0))
        self._ra_y_lim: float = np.tan(np.radians(self._ra_y_range / 2.0))

        self._x_scale: float = 2 * self._ra_x_lim / self._do_x_range
        self._y_scale: float = 2 * self._ra_y_lim / self._do_y_range

    def convert(self, dp: Cartesian) -> Polar:
        """Calculate the polar coordinates
        :param dp: the data points, tuple of (x,y)
        :type dp: Tuple[float, float]
        :returns: polar coordinates
        :rtype: (r , theta, phi)
        """
        x, y = dp
        dx, dy = x - self._do_ox, y - self._do_oy
        sdx, sdy = self._x_scale * dx, self._y_scale * dy

        theta = self._ra_ox + np.degrees(np.arctan(sdx))
        phi = self._ra_oy + np.degrees(np.arctan(sdy))

        r = np.sqrt(sdx * sdx + sdy * sdy + 1)

        return r, theta, phi
