import json
import os

from pages.common import *

hide_sidebar()
# Initialize session state for page navigation
st.session_state.page = 1  # Start at page 1
st.session_state.user_data = {}  # Dictionary to store user responses
st.session_state.inc_int = 0
st.session_state.question_idx = 0
st.session_state.example_idx = 0
st.session_state.user_pref_idx = 0

PLOT_PATH = "scatter_data"
st.session_state.plots = {
    int(ppath.split(".")[0]): json.load(open(os.path.join(PLOT_PATH, ppath), "r"))
    for ppath in os.listdir(PLOT_PATH)
}

st.session_state.questions = json.load(open("spatial_questions.json", "r"))
st.session_state.num_questions = len(
    [1 for q in st.session_state.questions if q["ttype"] == "question"]
)

# Page 1 - Collect Input
st.write(
    """# Data Sonification Using Spatial Audio
         """
)
st.image("./assets/images/tamu_logo.png", width=150)

st.write(
    """1. Our Research group is exploring the use of simulated spatial audio
         for data representation.
         """
)
st.write(
    """2. In this study, you will listen to some audio files, and decide the chart that 
         corresponds with the audio."""
)
st.write(
    f"""3. This test contains {st.session_state.num_questions} questions and shouldn't take longer than 20 minutes."""
)


affiliated = st.checkbox("I am affiliated with the research team")

if st.button("Continue", type="primary"):
    # Save responses in session state and move to next page
    st.session_state.user_data["affiliated"] = affiliated
    st.session_state.user_data["ref_number"] = get_new_ref()
    next_page()
