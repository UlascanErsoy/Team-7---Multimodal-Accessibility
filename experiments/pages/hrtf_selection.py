import os

from pages.common import *

hide_sidebar()


st.write(
    """This is a study about using **Directional Audio** in data encoding. To simulate directional audio using headphones, we must find the appropriate **settings** for you."""
)
st.write(
    """Listen to different settings by clicking the buttons. You should hear a sound coming from `behind` -> `above` -> `front and below`"""
)

st.write("""Pick the option that sounds the best to you""")

sex = st.session_state.user_data["sex"]
CIPIC_SUB_DIR = os.path.join("cipic_hrtf_database", sex.lower())


import base64
from io import BytesIO

from scipy.io import wavfile

import toph.audio.spatial
from toph.audio.playable import Chain, Silence, SineWave, Wave
from toph.audio.spatial import SpatialPanner
from toph.audio.stage import AudioStage
from toph.axis.spatial import LinearSpatialAxis


def play_test_sequence(cipic_path):

    with AudioStage() as stage:

        toph.audio.spatial.CIPIC_BASE_PATH = cipic_path

        seq = Chain(
            Wave(AUDIO_PATH).add_effect(SpatialPanner(0.0, 180.0, 2.0)),
            Silence(0.3),
            Wave(AUDIO_PATH).add_effect(SpatialPanner(0.0, 90.0, 2.0)),
            Silence(0.3),
            Wave(AUDIO_PATH).add_effect(SpatialPanner(0.0, -44.0, 2.0)),
            Silence(0.3),
        )

        arr = stage.get_ndarray(seq)
        v_file = BytesIO()
        wavfile.write(
            v_file,
            rate=stage.frame_rate,
            # todo: handle formats other than int16, make it better
            data=arr,
        )
        v_file.seek(0)
        b64 = base64.b64encode(v_file.read()).decode()

        md = f"""
            <audio style='display: none' controls autoplay="true">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            Audio
            </audio>
            """

        st.session_state.inc_int += 1
        print(st.session_state.inc_int)

        if st.session_state.inc_int % 2:
            st.write(".")

        st.markdown(
            md,
            unsafe_allow_html=True,
        )

        if st.session_state.inc_int % 2 == 0:
            st.write(".")


hrtfs = os.listdir(CIPIC_SUB_DIR)
cols = st.columns(len(hrtfs))

for idx, hrtf in enumerate(hrtfs):

    hrtf_id = hrtf.split(".")[0]
    btn = cols[idx].button(hrtf_id)

    if btn:
        play_test_sequence(os.path.join(CIPIC_SUB_DIR, hrtf))
        st.session_state.user_data["hrtf_id"] = hrtf_id
        st.write(f"Current selection: {hrtf_id}")

if st.button("Continue", type="primary"):
    next_page()
