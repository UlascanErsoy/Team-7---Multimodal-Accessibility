import base64
from io import BytesIO

import matplotlib.pyplot as plt
from pages.common import AUDIO_PATH
from scipy.io import wavfile

from toph.audio.effect import SimplePanner
from toph.audio.playable import Chain, Silence, SineWave, Wave
from toph.audio.spatial import SpatialPanner
from toph.audio.stage import AudioStage
from toph.axis.spatial import LinearSpatialAxis


def ax_gen(domain, range_):

    do_scale = max(domain) - min(domain)
    ra_scale = max(range_) - min(range_)

    def foo(dp):

        dx = dp - min(domain)
        sdx = dx / do_scale
        return min(range_) + sdx * ra_scale

    return foo


def sonify_y_ax(xs, ys, mode, gaps=0.5):
    """ """
    with AudioStage() as stage:

        space_ax = LinearSpatialAxis(
            domain=((min(xs), max(xs)), (min(ys), max(ys))),
            range_=((-50.0, 50.0), (-45.0, 90.0)),
        )

        # TODO: replace with linear axis when implemented
        lin_ax = ax_gen(domain=(min(ys), max(ys)), range_=(110, 880))

        simple_lr_ax = ax_gen(domain=(min(xs), max(xs)), range_=(-0.98, +0.99))

        marks = []

        for x, y in zip(xs, ys):

            if mode == "full_spatial":

                r, az, el = space_ax((x, y))

                marks.extend(
                    [
                        Wave(AUDIO_PATH).add_effect(SpatialPanner(az, el, r)),
                        Silence(secs=gaps),
                    ]
                )

            elif mode == "pitch":

                # keep the y as 0 to get a good r
                az = simple_lr_ax(x)
                freq = lin_ax(y)

                print(az, freq)
                marks.extend(
                    [
                        SineWave(vol=0.25, f=freq, secs=0.5).add_effect(
                            SimplePanner(dir=az)
                        ),
                        Silence(secs=gaps),
                    ]
                )

            elif mode == "both":
                # keep the y as 0 to get a good r
                r, az, el = space_ax((x, y))
                freq = lin_ax(y)

                marks.extend(
                    [
                        SineWave(vol=0.85, f=freq, secs=0.5).add_effect(
                            SpatialPanner(az, el, r)
                        ),
                        Silence(secs=gaps),
                    ]
                )

        return stage.get_ndarray(Chain(*marks))


def sonify_x_ax(xs, ys, x_mode, y_mode, gaps=0.5):
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

        return stage.get_ndarray(Chain(*marks))


def get_audio_comp(arr, frame_rate, visible=True, autoplay=False) -> str:
    """Takes an audio array
    returns an audio component
    """
    v_file = BytesIO()
    wavfile.write(
        v_file,
        rate=frame_rate,
        # todo: handle formats other than int16, make it better
        data=arr,
    )
    v_file.seek(0)
    b64 = base64.b64encode(v_file.read()).decode()

    md = f"""<audio {"style='display: none'" if not visible else ''} controls {'autoplay="true"' if autoplay else ''}>
        """
    src = f"""<source src="data:audio/wav;base64,{b64}" type="audio/wav">"""

    return md + src + "</audio>"


SONIFICATION_FUNCTIONS = {"sonify_y_ax": sonify_y_ax, "sonify_x_ax": sonify_x_ax}


def plot_four(datasets, idxs, xlim=None, ylim=None, s=75):
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))

    for i, ax in enumerate(axes.flat):
        ax.scatter(datasets[idxs[i]]["x"], datasets[idxs[i]]["y"], s=100)
        ax.set_title(f"Option {i + 1}")
        ax.grid(True)

        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)

        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    return fig
