"""Module for AudioStage"""

from typing import Optional

import pyaudio

from toph.audio.playable import Playable
from toph.audio.utils import int16_bytes


class AudioStage:
    """AudioStage is a wrapper for pyaudio,
    implements a context manager in addition to other utility
    functions to play nice with primitives provided by TOPH
    """

    # TODO: IDK maybe put somewhere
    CHUNK_SIZE = 1024

    def __init__(
        self, frame_rate: int = 44100, sample_width: int = 2, n_channels: int = 2
    ):
        """Initialize a sound stage
        :param frame_rate: frame rate for the audio track,
        defaults to CD quality 44100
        :type frame_rate: int
        :param sample_width: sample width in bytes (1,2,3,4)
        :type sample_width: int
        :param n_channels: number of channels (1,2)
        :type n_channels: int
        """
        self._pyaudio = pyaudio.PyAudio()
        self.frame_rate: int = frame_rate
        self.sample_width: int = sample_width
        self.n_channels: int = n_channels
        self._stream: Optional[pyaudio.Stream] = None

        if self.sample_width not in (1, 2, 3, 4):
            raise ValueError(f"sample_width {sample_width} must be 1,2,3,4.")

        if self.n_channels not in (1, 2):
            raise ValueError(f"n_channels {n_channels} must be 1 or 2.")

    def __enter__(self):
        """Entry method for the context manager"""
        self._stream = self._pyaudio.open(
            format=self._pyaudio.get_format_from_width(self.sample_width),
            channels=self.n_channels,
            rate=self.frame_rate,
            output=True,
        )

        # do we need to do the thing where we store the old values
        # and do the switcheroo
        Playable.FRAME_RATE = self.frame_rate
        Playable.SAMPLE_WIDTH = self.sample_width
        Playable.N_CHANNELS = self.n_channels

        return self

    def play(self, p: Playable):
        """ """
        if not isinstance(p, Playable):
            raise TypeError("AudioStage can only consume Playable objects")

        for chunk in p.consume(self.CHUNK_SIZE):
            self._stream.write(int16_bytes(chunk))

    def __exit__(self, type_, value, traceback):
        """Exit method for the context manager"""
        self._stream.stop_stream()
        self._stream.close()
        self._pyaudio.terminate()
