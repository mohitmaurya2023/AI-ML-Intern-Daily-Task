import streamlit as st

with open("styles/login.css") as f:
    st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)


st.title("About Page")
st.write("---")
st.write("Welcome to About Page.")
st.balloons()
st.markdown("""<style>
            body {
            background: cyan;
            }
            </style>""", unsafe_allow_html=True)