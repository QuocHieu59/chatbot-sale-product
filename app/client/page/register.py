import streamlit as st
from api_call import register
from utils.helper_link import link 

def register_page():
    st.header("Đăng ký")
    with st.form("register_form"):
        name = st.text_input("Họ và tên")
        email = st.text_input("Email")
        age = st.number_input("Tuổi", min_value=1, max_value=120, step=1)
        password = st.text_input("Mật khẩu", type="password")
        repeat_password = st.text_input("Xác nhận mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng ký")

        if submitted:
            user = register(name, email, password, age, repeat_password)
            if user:
                st.success("Đăng ký thành công!")
                st.query_params.page = "login"
                st.rerun()
            else:
                st.error("Đăng ký thất bại!")
        link("👉 Quay lại đăng nhập", "login")
