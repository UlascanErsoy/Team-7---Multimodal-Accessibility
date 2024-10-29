"""Example using chains and tracks
Chains combine audio sources sequentially
Tracks combine them in a parallel manner
"""

from toph.audio.playable import Chain, MultiTrack, Silence, SineWave, Wave
from toph.audio.stage import AudioStage

if __name__ == "__main__":

    with AudioStage() as stage:

        tracks = MultiTrack(
            Chain(
                Silence(secs=0.8),
                SineWave(vol=0.1, f=440, secs=2),
                Silence(secs=1.0),
            ),
            Chain(
                SineWave(vol=0.1, f=330, secs=0.5),
                Silence(secs=0.3),
                SineWave(vol=0.1, f=220, secs=2),
                Silence(secs=1.0),
            ),
        )

        tracks2 = MultiTrack(
            Wave("examples/assets/jazz.wav"),
            Chain(Silence(secs=1.0), SineWave(vol=0.1, f=440, secs=1.0)),
            Chain(SineWave(vol=0.1, f=440, secs=1.0)),
            Silence(secs=1.0),
        )

        chain = Chain(tracks, tracks2)

        stage.play(chain)
