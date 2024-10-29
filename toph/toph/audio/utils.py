"""Utility functions for audio processing"""

import numpy as np


def int16_bytes(arr: np.ndarray) -> bytes:
    """Takes a function that returns a np.ndarray
    turns it into a bytes array returning function
    """
    arr *= 32767
    arr = np.int16(arr)
    return arr.tobytes()
