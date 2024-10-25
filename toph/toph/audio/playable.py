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
    def consume(self, chunk_size: int) -> bytes:
        """The Stage class consumes the data
        using this class.
        """
        raise NotImplementedError("The consume method needs to be implemented")


class SineWave(Playable):
    """The simplest sine generator"""

    def __init__(self, vol: float, f: int, secs: float):
        """
        :param f: frequency in hz
        :type f: int
        :param vol: volume (0, 1)
        :type vol: float
        :param secs: how many seconds should it last
        :type secs: int
        """
        self.secs: float = secs
        self.vol: float = vol
        self.f: int = f
        super().__init__()

    def consume(self, chunk_size: int) -> np.ndarray:
        """Consume the sine wave"""
        total_frames = int(self.secs * self.FRAME_RATE)
        samples = np.linspace(0, self.secs, total_frames, endpoint=False)
        signal = self.vol * np.sin(2 * np.pi * self.f * samples)
        signal = self._apply_effects(signal)
        cursor = 0

        while cursor <= samples.shape[0]:
            yield signal[cursor : min(cursor + chunk_size, total_frames)]
            cursor += chunk_size


class Silence(Playable):
    """The simplest silence generator"""

    def __init__(self, secs: float):
        """
        :param secs: duration
        :type secs: int
        """
        self.secs: float = secs
        super().__init__()

    def consume(self, chunk_size: int) -> np.ndarray:
        """Consume the silence"""
        cursor = 0
        while cursor <= int(self.secs * self.FRAME_RATE):
            yield np.zeros(min(chunk_size, int(self.secs * self.FRAME_RATE) - cursor))
            cursor += chunk_size


class Chain(Playable):
    """Chain playables sequentially"""

    def __init__(self, *args):
        """Takes a list of playables chains
        them back to back
        """
        self.chain: List[Playable] = args
        super().__init__()

        if any([not isinstance(arg, Playable) for arg in args]):
            raise TypeError("All arguments must be playables")

    def consume(self, chunk_size: int) -> np.ndarray:
        """Consume the chain"""
        for p in self.chain:
            for chunk in p.consume(chunk_size):
                yield self._apply_effects(chunk)


class MultiTrack(Playable):
    """MultiTrack class"""

    def __init__(self, *args):
        """Takes a list of playables and
        consumes them simultaneously
        """
        self.tracks: List[Playable] = args
        super().__init__()

    def consume(self, chunk_size: int) -> np.ndarray:
        """Consume the MultiTrack"""
        gens = [gen.consume(chunk_size) for gen in self.tracks]

        base = np.zeros((chunk_size,))
        terms = [True] * len(gens)

        while any(terms):
            base = np.zeros((chunk_size,))
            for idx, gen in enumerate(gens):
                try:
                    data = next(gen)
                except StopIteration:
                    data = np.zeros((chunk_size,))
                    terms[idx] = False

                if data.shape[0] < chunk_size:
                    data = np.pad(
                        data, (0, chunk_size - data.shape[0]), mode="constant"
                    )

                base += data

            yield base
