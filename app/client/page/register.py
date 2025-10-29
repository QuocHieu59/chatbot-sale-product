import streamlit as st
from api_call import register
from utils.helper_link import link 

def register_page():
    st.header("Register")
    with st.form("register_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        password = st.text_input("Password", type="password")
        repeat_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            user = register(name, email, password, age, repeat_password)
            if user:
                st.success("Registration successful!")
                st.query_params.page = "login"
                st.rerun()
            else:
                st.error("Registration failed!")
        link("👉 Back to Login", "login")
