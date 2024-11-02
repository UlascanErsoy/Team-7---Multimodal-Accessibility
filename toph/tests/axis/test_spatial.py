"""Tests for spatial axis stuff"""

import numpy as np
import pytest

from toph.axis.spatial import LinearSpatialAxis


@pytest.fixture
def ax():
    return LinearSpatialAxis(domain=((-5, 10), (-5, 5)), range_=((-60, 60), (-50, 40)))


def test_derived_domain(ax):
    """Test the derived values calculated in the
    initializer
    """
    assert ax._do_x_range == 15
    assert ax._do_y_range == 10
    assert ax._do_ox == 2.5
    assert ax._do_oy == 0.0


def test_derived_range(ax):
    """Test the derived values calculated in the
    initializer
    """
    assert ax._ra_x_range == 120
    assert ax._ra_y_range == 90
    assert ax._ra_ox == 0.0
    assert ax._ra_oy == -5.0

    assert pytest.approx(ax._ra_x_lim, 0.1) == np.sqrt(3)
    assert pytest.approx(ax._ra_y_lim, 0.1) == 1.0


data_points = [
    # domain , target
    ((10.0, 5), (60.0, 40.0)),
    ((-5.0, -5), (-60, -50)),
    ((2.5, 0.0), (0.0, -5.0)),
]


@pytest.mark.parametrize("domain,target", data_points)
def test_limits(ax, domain, target):
    """Test the derived scaling values from both domain
    and range
    """
    # TODO: maybe some tests for distance as well?
    _, theta, phi = ax(domain)

    assert pytest.approx(theta, 0.1) == target[0]
    assert pytest.approx(phi, 0.1) == target[1]
