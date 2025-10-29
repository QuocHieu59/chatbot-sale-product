import streamlit as st

def link(label: str, page: str):
    st.markdown(
        f'<a href="?page={page}" target="_self">{label}</a>',
        unsafe_allow_html=True
    )