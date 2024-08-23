import streamlit as st


with open("styles/login.css") as f:
    st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)


# Create a title
st.title("Analysis Page")
st.write("---")
# Add some text
st.write("Welcome to analysis Page.")
st.balloons()