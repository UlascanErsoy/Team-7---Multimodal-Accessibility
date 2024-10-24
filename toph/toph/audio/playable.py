"""Default playables for toph"""

from abc import ABC
from typing import List

import numpy as np

from toph.audio.effect import Effect


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

    def __init__(self, *args, **kwargs):
        """Base init class for playables"""
        self._effects: list = []

    def add_effect(self, *args) -> "Playable":
        """Add effects to the list"""
        if any([not isinstance(arg, Effect) for arg in args]):
            raise TypeError("All effects must be Effect type")

        self._effects.extend(args)

        return self

    def _apply_effects(self, data: np.ndarray) -> np.ndarray:
        """Utility class to apply all effects
        :param data: the soundwave
        :type data: ndarray
        :returns: new soundwave
        :rtype: ndarray
        """
        for effect in self._effects:
            data = effect.apply(data)

        return data

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
        super().__init__()

    def consume(self, len: int) -> np.ndarray:
        """Consume the sine wave"""
        total_frames = int(self.secs * self.FRAME_RATE)
        samples = np.linspace(0, self.secs, total_frames, endpoint=False)
        signal = np.sin(2 * np.pi * self.f * samples)
        signal = self._apply_effects(signal)
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
        super().__init__()

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
        super().__init__()

        if any([not isinstance(arg, Playable) for arg in args]):
            raise TypeError("All arguments must be playables")

    def consume(self, len: int) -> np.ndarray:
        """Consume the chain"""
        for p in self.chain:
            for chunk in p.consume(len):
                yield self._apply_effects(chunk)
