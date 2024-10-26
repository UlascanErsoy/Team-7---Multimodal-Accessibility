"""For testing purposes"""

import numpy as np

from toph.audio.effect import SimplePanner
from toph.audio.playable import Chain, Silence, SineWave
from toph.audio.stage import AudioStage


def bar(x, y, bars=1.5, gaps=0.5, ylims=(110, 880)):
    """Sonifies a bar"""

    sonics = []
    y_min, y_max = min(y), max(y)
    x_min, x_max = min(x), max(x)

    for idx in range(len(y)):
        freq = int(
            ylims[0] + (ylims[1] - ylims[0]) * ((y[idx] - y_min) / (y_max - y_min))
        )

        place = -1 + 2 * (x[idx] - x_min) / (x_max - x_min)

        sonics.append(
            SineWave(vol=0.5, f=freq, secs=bars).add_effect(SimplePanner(dir=place))
        )
        if idx < len(y) - 1:
            diff = np.abs(x[idx + 1] - x[idx])
            sonics.append(Silence(secs=gaps * diff))

    with AudioStage() as stage:
        chain = Chain(*sonics)
        stage.play(chain)
