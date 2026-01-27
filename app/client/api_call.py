import streamlit as st
import requests
import time
import os
from schema.database import ChatSession
from typing import List

from dotenv import load_dotenv
from schema.schema import ChatMessage



ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_user_chat_sessions(user_id: str) -> List[ChatSession]:
    """Get user's chat sessions."""
    try:
        response = requests.get( 
            f"{get_agent_url()}/messages/users/{user_id}/chat-sessions",
            verify=False
        )
        response.raise_for_status()
        return response.json()["sessions"]
    except Exception as e:
        st.error(f"Failed to get chat sessions: {str(e)}")
        return []
    
def get_chat_messages(session_id: str) -> List[ChatMessage]:
    """Get all messages from a chat session, sorted by sent_at."""
    try:
        response = requests.get(f"{get_agent_url()}/messages/chat-sessions/{session_id}/combined-messages", verify=False)
        response.raise_for_status()
        combined_messages = response.json()["messages"]

        # Convert to ChatMessage and sort by sent_at
        chat_messages = []
        for msg in combined_messages:
            chat_messages.append(ChatMessage(
                type=msg["type"],
                content=msg["content"],
                run_id=None  # No run_id in combined messages
            ))
        # Sort by sent_at if available
        combined_messages_sorted = sorted(
            zip(chat_messages, combined_messages),
            key=lambda x: x[1].get("sent_at") or ""
        )
        return [cm[0] for cm in combined_messages_sorted]
    except Exception as e:
        st.error(f"Error fetching chat messages: {str(e)}")
        return []

def get_agent_url() -> str:
    """Get the agent service URL from environment variables."""
    load_dotenv()
    agent_url = os.getenv("AGENT_URL")
    if not agent_url:
        host = os.getenv("HOST", "127.0.0.1")
        port = os.getenv("PORT", 8000)
        agent_url = f"https://{host}:{port}"
    return agent_url

def login(email, password, controller):
    res = requests.post(f"{get_agent_url()}/auth/login", json={"email": email, "password": password}, verify=False)
    data = res.json()
    if res.status_code == 200:
        st.session_state["logged_in"] = True
        controller.set(
        'access_token_user',
        data["data"]["access_token"],
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path='/'
        )
        role = data["data"]["user"]["role"]
        controller.set(
            'refresh_token_user',
            data["data"]["refresh_token"],
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path='/'
        )
        #access_token = controller.get('access_token_user')
        #print("Access token:", access_token)
        return role
    else:
        return ""

def register(name, email, password, age, repeat_password):
    res = requests.post(f"{get_agent_url()}/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
        "age": age,
        "repeat_password": repeat_password
    }, verify=False)
    if res.status_code == 200:
        st.success("✅ Đăng ký thành công! Vui lòng đăng nhập.")
        return True
    else:
        st.error(f"Lỗi đăng ký: {res.json().get('detail', 'Unknown error')}")
        return False


def refresh_access_token(refresh_access_user, controller):
    if not refresh_access_user:
        return False
    res = requests.get(f"{get_agent_url()}/auth/refresh", json={"refresh_token": refresh_access_user}, verify=False)
    if res.status_code == 200:
        data = res.json()
        controller.set('access_token_user', data["access_token"], max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, path='/') 
        return True
    else:
        st.warning("Refresh token hết hạn, vui lòng đăng nhập lại.")
        logout()
        return False

def check_login_status(access_token):
    """Kiểm tra cookie HttpOnly từ backend xem còn hợp lệ không"""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        resp = st.session_state.session.get(f"{get_agent_url()}/auth/me",timeout=5, headers=headers)
        data = resp.json()
        if resp.status_code == 401:
            st.info("⏱ Token hết hạn, đang refresh...")
            if refresh_access_token():
                return True
            return False
        if resp.logged_in:
            return True
        else:
            return False
    except Exception:
        return False
# def get_profile():
#     token = st.session_state.get("access_token")
#     headers = {"Authorization": f"Bearer {token}"}
#     res = requests.get(f"{API_URL}/users/me", headers=headers)

#     if res.status_code == 401:
#         st.info("⏱ Token hết hạn, đang refresh...")
#         if refresh_access_token():
#             # thử lại sau khi refresh
#             return get_profile()
#         return None
#     elif res.status_code == 200:
#         return res.json()
#     else:
#         st.error("Lỗi khi lấy dữ liệu người dùng.")
#         return None

def logout(controller):
    requests.post(f"{get_agent_url()}/auth/logout", verify=False)
    controller.remove('access_token_user', path='/')
    controller.remove('refresh_token_user', path='/')
    print("Logging out, clearing session state...")
    print("access_token_user after removal:", controller.get('access_token_user'))
     
    time.sleep(0.1)
    
    

def get_username_by_id(access_token_user):
    #print("Fetching user data with access token:", access_token_user)
    if not access_token_user:
        st.error("No access token provided.")
        return None
    headers = {"Authorization": f"Bearer {access_token_user}"}
    res = requests.get(f"{get_agent_url()}/auth/me", headers=headers, verify=False)
    if res.status_code == 200:
        data = res.json()
        user_data = data.get("data", {})
        username = user_data.get("name", "Người dùng")
        userid = user_data.get("id", "")
        userrole = user_data.get("role", "user")
        return username, userid, userrole
    else:
        st.error("Failed to fetch user data.")
        return None, None
    
async def send_message(messages, user_input, agent_client):
    # user_message = st.session_state.user_input
        # st.session_state.user_input = ""
    messages.append(ChatMessage(type="human", content=user_input))
        #st.session_state.messages.append(ChatMessage(type="human", content=user_message))            
    
    
        #st.session_state.messages.append(ChatMessage(type="ai", content="Đây là câu trả lời giả lập từ trợ lý AI."))

