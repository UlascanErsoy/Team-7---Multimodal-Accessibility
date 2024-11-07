from pages.common import *

hide_sidebar()
# Page 1 - Collect Input
st.write("### Page 2: Additional Information")
st.write("Name:", st.session_state.user_data.get("name"))
st.write("Age:", st.session_state.user_data.get("age"))

occupation = st.text_input("Enter your occupation:")

if st.button("Submit Page 2"):
    # Save additional response and move to next page
    st.session_state.user_data["occupation"] = occupation
    next_page()

# Page 3 - Final Page
