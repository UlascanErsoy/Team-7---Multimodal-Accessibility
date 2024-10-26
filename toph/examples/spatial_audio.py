"""Example using a simple effect"""

from toph.audio.playable import Chain, Wave
from toph.audio.spatial import SpatialPanner
from toph.audio.stage import AudioStage

if __name__ == "__main__":

    with AudioStage() as stage:

        ding_path = "examples/assets/ding.wav"

        az = Chain(
            *[
                Wave(ding_path).add_effect(SpatialPanner(val, 25.0))
                for val in range(-80, 80, 5)
            ]
        )
        el = Chain(
            *[
                Wave(ding_path).add_effect(SpatialPanner(0.0, val))
                for val in range(-150, 50, 5)
            ]
        )

        stage.play(Chain(az, el))
