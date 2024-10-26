"""Example using a simple effect"""

from toph.audio.effect import SimplePanner
from toph.audio.playable import Chain, Wave
from toph.audio.stage import AudioStage

if __name__ == "__main__":

    with AudioStage() as stage:

        ding_path = "examples/assets/ding.wav"

        chain = Chain(
            Wave(ding_path).add_effect(SimplePanner(dir=-1.0)),
            Wave(ding_path).add_effect(SimplePanner(dir=-0.5)),
            Wave(ding_path).add_effect(SimplePanner(dir=0.0)),
            Wave(ding_path).add_effect(SimplePanner(dir=0.5)),
            Wave(ding_path).add_effect(SimplePanner(dir=1.0)),
        )

        stage.play(chain)
