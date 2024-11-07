from pages.common import *

hide_sidebar()

import os

import matplotlib.pyplot as plt
from pages.sonification_utils import (SONIFICATION_FUNCTIONS, get_audio_comp,
                                      plot_four)

last_example = getattr(st.session_state, "last_example", {})
cur_q = st.session_state.question_idx
cur_e = st.session_state.example_idx
cur_u = st.session_state.user_pref_idx

total = st.session_state.num_questions


if cur_q + cur_e + cur_u < len(st.session_state.questions):
    cur_data = st.session_state.questions[cur_q + cur_e + cur_u]
else:  # questions are over submit and redirect to final screen
    from pages.db import submit_json_to_sheets

    submit_json_to_sheets(st.session_state.user_data)
    next_page()

prog = min((cur_q + 1) / total, 1.0)
st.progress(prog, text=f"{cur_q}/{total}")


print(st.session_state.user_data)

if cur_data["ttype"] == "Example":

    st.session_state.last_example = cur_data
    st.write("# Example")
    st.write(cur_data["explanation"])
    # render the plot
    plot_data = st.session_state.plots[cur_data["plot"]]

    son_fn = SONIFICATION_FUNCTIONS[cur_data["sonify"]]

    son_arr = son_fn(plot_data["x"], plot_data["y"], **cur_data["args"])

    aud_comp = get_audio_comp(son_arr, 44100)

    st.markdown(
        aud_comp,
        unsafe_allow_html=True,
    )

    # plot the example
    fig, ax = plt.subplots()
    ax.scatter(plot_data["x"], plot_data["y"], s=100)
    ax.set_xlim([-0.2, 9.2])
    ax.set_ylim([-0.05, 1.05])

    ax.set_xticks([])
    ax.set_yticks([])

    st.pyplot(fig)

    btn_text = "Skip"

    if st.button("Start", type="primary"):
        st.session_state.example_idx += 1
        switch_page("questions")

elif cur_data["ttype"] == "user_preference":
    st.write("# Preference Question")
    st.write(cur_data["explanation"])

    cols = st.columns(len(cur_data["options"]))

    for idx, col in enumerate(cols):

        if col.button(cur_data["options"][idx], type="primary"):
            st.session_state.user_data[f"UserPref_{idx}"] = cur_data["options"][idx]
            st.session_state.user_pref_idx += 1
            switch_page("questions")


else:
    st.write("# Question")

    fig = plot_four(
        st.session_state.plots, cur_data["plots"], xlim=[-0.5, 9.5], ylim=[-0.05, 1.05]
    )

    st.pyplot(fig)

    plot_data = st.session_state.plots[cur_data["answer"]]
    # sonify the answer
    son_fn = SONIFICATION_FUNCTIONS[last_example["sonify"]]
    son_arr = son_fn(plot_data["x"], plot_data["y"], **last_example["args"])
    aud_comp = get_audio_comp(son_arr, 44100, visible=False, autoplay=True)

    play_count_idx = f"Q{cur_q}_PlayCount"

    if play_count_idx not in st.session_state.user_data:
        st.session_state.user_data[play_count_idx] = 0

    if play_btn := st.button(
        f"Play Audio (Only Once)", disabled=st.session_state.user_data[play_count_idx]
    ):

        st.session_state.inc_int += 1

        if st.session_state.inc_int % 2:
            st.write(".")

        st.markdown(
            aud_comp,
            unsafe_allow_html=True,
        )

        if st.session_state.inc_int % 2 == 0:
            st.write(".")

    # answer stuff
    if st.session_state.user_data[play_count_idx]:

        cols = st.columns(4)
        answer_idx = f"Q{cur_q}_Answer"
        correct_idx = f"Q{cur_q}_Correct"
        for idx, col in enumerate(cols):
            if col.button(f"{idx+1}", type="primary"):
                st.session_state.question_idx += 1
                cplot = cur_data["plots"][idx]
                st.session_state.user_data[answer_idx] = cplot
                st.session_state.user_data[correct_idx] = cplot == cur_data["answer"]
                switch_page("questions")

    st.session_state.user_data[play_count_idx] += 1
