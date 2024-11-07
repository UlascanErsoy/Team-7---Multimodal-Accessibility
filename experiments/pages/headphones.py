from pages.common import *

hide_sidebar()

st.write(
    """- Thank you for joining our study. We just need to ask a few preliminary questions
         to find the best **settings** for you!"""
)

st.write(
    f"""- If you run into any issues or have any questions for the research team,
         your reference number is **{st.session_state.user_data['ref_number']}**"""
)

st.write("# Headphones")

st.write("For this part of study, we are mainly focusing on `in-ear` headpones")
st.write("However, if you only have `over-the-ear` ones we still accept submissions.")

st.write("**For reference:**")

st.image("assets/images/headphone_types.png", width=400)


headphones = st.selectbox("Headphone Type:", ("In-ear", "Over-the-ear"))

age = st.number_input("Age:", min_value=9, max_value=99)
sex = st.selectbox("Sex:", ("Male", "Female"))

if st.button("Continue", type="primary"):
    # Save responses in session state and move to next page
    st.session_state.user_data["headphone_type"] = headphones
    st.session_state.user_data["sex"] = sex
    st.session_state.user_data["age"] = age
    next_page()
