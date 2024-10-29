"""This is the simplest example file. It loads a stage, and plays a sine wave"""

from toph.audio.playable import SineWave
from toph.audio.stage import AudioStage

if __name__ == "__main__":

    with AudioStage() as stage:
        stage.play(SineWave(f=440, secs=2, vol=0.1))
