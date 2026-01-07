import streamlit as st

def link(label: str, page: str):
    st.markdown(
        f'<a href="?page={page}" target="_self">{label}</a>',
        unsafe_allow_html=True
    )

def group_last(messages, limit=10):
    pairs = []
    current_human = None

    for msg in messages:
        if msg.type == "human":
            pairs.append({"role":"user","content": msg.content})
            current_human = msg.content
        elif msg.type == "ai" and current_human:
            pairs.append({"role":"user","content": msg.content})

    print("Các cặp hội thoại gần nhất:", pairs)

    # chỉ lấy 5 cặp gần nhất
    return pairs[-limit:]