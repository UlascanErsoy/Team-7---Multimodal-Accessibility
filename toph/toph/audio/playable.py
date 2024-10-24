"""Default playables for toph"""

from abc import ABC
from typing import List

import numpy as np


class Playable(ABC):
    """Base playable class for toph,
    anything that needs to be fed into a
    Stage class needs to inherit this
    (directly or indirectly).
    """

    # should these be capitalized(?) (technically constants)
    FRAME_RATE = 44100
    CHANNELS = 2
    SAMPLE_WIDTH = 2

    # should return bytes or should the AudioStage handle this ?
    def consume(self, len: int) -> bytes:
        """The Stage class consumes the data
        using this class.
        """
        raise NotImplementedError("The consume method needs to be implemented")


class SineWave(Playable):
    """The simplest sine generator"""

    def __init__(self, f: int, secs: float):
        """
        :param f: frequency in hz
        :type f: int
        :param secs: how many seconds should it last
        :type secs: int
        """
        self.secs: float = secs
        self.f: int = f

    def consume(self, len: int) -> np.ndarray:
        """Consume the sine wave"""
        total_frames = int(self.secs * self.FRAME_RATE)
        samples = np.linspace(0, self.secs, total_frames, endpoint=False)
        signal = np.sin(2 * np.pi * self.f * samples)
        cursor = 0

        while cursor <= samples.shape[0]:
            yield signal[cursor : min(cursor + len, total_frames)]
            cursor += len


class Silence(Playable):
    """The simplest silence generator"""

    def __init__(self, secs: float):
        """
        :param secs: duration
        :type secs: int
        """
        self.secs: float = secs

    def consume(self, len: int) -> np.ndarray:
        """Consume the silence"""
        cursor = 0
        while cursor <= int(self.secs * self.FRAME_RATE):
            yield np.zeros(min(len, int(self.secs * self.FRAME_RATE) - cursor))
            cursor += len


class Chain(Playable):
    """Chain playables together"""

    def __init__(self, *args):
        """Takes a list of playables chains
        them back to back
        """
        self.chain: List[Playable] = args

        if any([not isinstance(arg, Playable) for arg in args]):
            raise TypeError("All arguments must be playables")

    def consume(self, len: int) -> np.ndarray:
        """Consume the chain"""
        for p in self.chain:
            for chunk in p.consume(len):
                yield chunk
