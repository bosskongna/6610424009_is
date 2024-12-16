import streamlit as st
# st.title("Login Page")
# st.image("assets/logo.png", width=100)
def show():
    st.title("Login Page")
    st.image("assets/logo.png", width=100)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.success("Welcome back!")