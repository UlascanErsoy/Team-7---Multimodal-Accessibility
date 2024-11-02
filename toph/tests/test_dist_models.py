"""Tests for distance models"""

from toph.audio.distance import IPLDistanceModel


def test_one_r():
    """Test that one r distance results in no
    power loss
    """
    model = IPLDistanceModel()

    assert model(r=1.0) == 1
