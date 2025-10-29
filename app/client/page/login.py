import streamlit as st
from api_call import login
from utils.helper_link import link



def login_page(controller):
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = login(email, password, controller)
            if user:
                st.success("Login successful!")
                st.query_params.page = "home"
                st.rerun()
            else:
                st.error("Invalid email or password!")
        link("👉 Register here", "register")