import streamlit as st

with open("styles/dashboard.css") as f:
    st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)



st.title("StockAI")
st.write("---")

st.write("Welcome to Dashborad.")
st.balloons()