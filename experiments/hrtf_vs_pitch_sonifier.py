import matplotlib.pyplot as plt

from toph.audio.effect import SimplePanner
from toph.audio.playable import Chain, Silence, SineWave, Wave
from toph.audio.stage import AudioStage

AUDIO_PATH = "assets/ding.wav"


def ax_gen(domain, range_):

    do_scale = max(domain) - min(domain)
    ra_scale = max(range_) - min(range_)

    def foo(dp):

        dx = dp - min(domain)
        sdx = dx / do_scale
        return min(range_) + sdx * ra_scale

    return foo


def sonify(xs, ys, x_mode, y_mode, gaps=0.5, save=None):
    """ """
    with AudioStage(frame_rate=48000) as stage:

        # TODO: replace with linear axis when implemented

        lin_ax = ax_gen(domain=(min(xs), max(xs)), range_=(-1.0, +1.0))

        pitch_ax = ax_gen(domain=(min(ys), max(ys)), range_=(110, 880))

        x_deltas = [xs[idx + 1] - xs[idx] for idx in range(len(xs) - 1)]
        x_deltas.append(0.0)

        gap_ax = ax_gen(domain=(min(x_deltas), max(x_deltas)), range_=(0.25, 1.25))

        marks = []

        for idx, (x, y) in enumerate(zip(xs, ys)):

            audio_src = (
                Wave(AUDIO_PATH)
                if y_mode == "static"
                else SineWave(vol=0.85, f=pitch_ax(y), secs=0.5)
            )
            if x_mode == "spatial":

                marks.extend(
                    [
                        audio_src.add_effect(SimplePanner(dir=lin_ax(x))),
                        Silence(secs=gaps),
                    ]
                )

            elif x_mode == "gaps":

                marks.append(audio_src)
                if x_deltas[idx] > 0.0:
                    marks.append(Silence(secs=gap_ax(x_deltas[idx])))

        if save:
            stage.save(Chain(*marks), save)

        else:
            stage.play(Chain(*marks))


def plot_four(datasets, idxs, y_mode, show_correct=None):
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))

    for i, ax in enumerate(axes.flat):
        ax.scatter(
            datasets[idxs[i]]["x"],
            (
                datasets[idxs[i]]["y"]
                if y_mode == "pitch"
                else [0] * len(datasets[idxs[i]]["x"])
            ),
        )
        ax.set_title(f"Plot {i + 1}")
        ax.grid(True)

        if show_correct is not None:
            for spine in ax.spines.values():
                if idxs[i] == show_correct:
                    spine.set_linewidth(2)
                    spine.set_color("green")
                else:
                    spine.set_color("red")

    plt.tight_layout()


datasets = [
    {"x": [0, 10, 30, 40, 90], "y": [10, 15, 20, 15, 10]},
    {"x": [0, 10, 20, 30, 40], "y": [10, 15, 20, 15, 10]},
    {"x": [0, 10, 20, 40, 80, 160], "y": [20, 15, 20, 15, 10, 5]},
    {"x": [0, 5, 15, 30, 45, 60], "y": [12, 14, 19, 14, 11, 8]},
    {"x": [0, 20, 40, 60, 80, 100], "y": [15, 20, 25, 20, 15, 10]},
    {"x": [0, 15, 35, 55, 75, 95], "y": [10, 18, 16, 20, 15, 12]},
    {"x": [0, 12, 25, 50, 75, 100], "y": [8, 12, 18, 22, 18, 10]},
    {"x": [0, 25, 50, 75, 100, 125], "y": [20, 18, 22, 18, 14, 10]},
]
