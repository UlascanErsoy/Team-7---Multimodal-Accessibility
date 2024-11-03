"""Example using a linear axis"""

from toph.audio.playable import Chain, Silence, Wave
from toph.audio.spatial import SpatialPanner
from toph.audio.stage import AudioStage
from toph.axis.spatial import LinearSpatialAxis

if __name__ == "__main__":

    xs = [0, 1, 2, 3, 4, 5]
    ys = [0, 10, 20, 50, 30, 10]

    with AudioStage() as stage:

        ding_path = "examples/assets/ding.wav"

        axis = LinearSpatialAxis(
            domain=((min(xs), max(xs)), (min(ys), max(ys))),
            range_=((-50.0, 50.0), (-45.0, 90.0)),
        )

        playables = []
        for x, y in zip(xs, ys):
            r, theta, phi = axis((x, y))

            print(r, theta, phi)

            playables.extend(
                [
                    Wave(ding_path).add_effect(SpatialPanner(theta, phi, r)),
                    Silence(secs=0.2),
                ]
            )

        stage.play(Chain(*playables))
