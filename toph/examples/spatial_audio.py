"""Example using a simple effect"""

from toph.audio.playable import Chain, Wave
from toph.audio.spatial import SpatialPanner
from toph.audio.stage import AudioStage


def calc_dist(max_dist: float, max_angle: float, angle: float):
    return 1 + max_dist - max_dist * (1 - abs(angle) / max_angle)


if __name__ == "__main__":

    with AudioStage() as stage:

        ding_path = "examples/assets/ding.wav"

        az = Chain(
            *[
                Wave(ding_path).add_effect(
                    SpatialPanner(val, 25.0, calc_dist(3.0, 80.0, val))
                )
                for val in range(-80, 80, 5)
            ]
        )
        el = Chain(
            *[
                Wave(ding_path).add_effect(
                    SpatialPanner(0.0, val, calc_dist(5.0, 230.0, val))
                )
                for val in range(-45, 230, 5)
            ]
        )

        stage.play(Chain(az, el))
