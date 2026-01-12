import streamlit as st
from api_call import login
from utils.helper_link import link

def login_page(controller):
    st.header("Đăng nhập")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")

        if submitted:
            user = login(email, password, controller)
            if user:
                st.success("Đăng nhập thành công!")
                st.query_params.page = "home"
                st.rerun()
            else:
                st.error("Email hoặc mật khẩu không hợp lệ!")
        link("👉 Bạn chưa có tài khoản? Đăng ký tài khoản", "register")