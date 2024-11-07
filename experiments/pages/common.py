import uuid

import streamlit as st
from streamlit_extras.switch_page_button import switch_page


# hide sidebar
def hide_sidebar():
    st.set_page_config(initial_sidebar_state="collapsed")

    st.markdown(
        """
    <style>
        [data-testid="stSidebarCollapsedControl"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


# Define a function to move to the next page
pages = {2: "headphones", 3: "hrtf_selection", 4: "questions"}


def next_page():
    st.session_state.page += 1
    switch_page(pages.get(st.session_state.page, "final"))


def get_new_ref():
    return str(uuid.uuid4()).upper().split("-")[0]


AUDIO_PATH = "assets/snare3.wav"
