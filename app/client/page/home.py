import streamlit as st
from api_call import logout, get_username_by_id, send_message, get_agent_url
from service.agent_service.clientAgent_service import AgentClient, AgentClientError
from schema.schema import ChatHistory, ChatMessage
import streamlit.components.v1 as components
import uuid
APP_TITLE = "Hieu's AI Assistant"
APP_ICON = "🤖"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def display_messages(messages):
    st.markdown("""
    <style>
    /* Target chính xác container chính */
    div[data-testid="stMainBlockContainer"] {
        width: 100%;
        padding: 1rem 1rem 1rem !important; /* chỉnh lại padding */
        max-width: 1000px !important;       /* ví dụ muốn rộng hơn */
        margin: 0 auto;
        background-color: #f9f9f9;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    chat_html = ""
    # messages: list[ChatMessage] = st.session_state.messages
    
    # if len(messages) == 0:
    #     WELCOME = "Hello! I'm a simple chatbot. Ask me anything!"
    # with st.chat_message("ai"):
    #     st.write(WELCOME)
    # if len(messages) == 0:
    # print("==============")
    # print(messages)
    for i, message in enumerate(messages):
        role = message.type
        content = message.content
        avatar_url = (
            "https://api.dicebear.com/7.x/bottts/svg?seed=assistant"
            if role == "ai"
            else "https://api.dicebear.com/7.x/personas/svg?seed=user"
        )
        chat_html += f"""
        <div class="chat-message {role}">
            <div class="message-content">
                <img class="avatar" src="{avatar_url}">
                <div class="text">{content}</div>
            </div>
        </div>
        """

    full_html = f"""
    <html>
    <head>
        <style>
            [data-testid="stMainBlockContainer"] > div:first-child {{
            width: 100%;
            padding: 1rem;
            max-width: 900px;
            margin: 0 auto;
            }}
            .chat-container {{
                height: 420px;
                overflow-y: auto;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 10px;
                background-color: #1e1e1e;
                color: white;
                scroll-behavior: smooth; /* ✅ cuộn mượt */
                font-family: "Segoe UI", sans-serif;
            }}
            .chat-message {{
                padding: 0.5rem;
                border-radius: 0.5rem;
                margin-bottom: 0.5rem;
                display: flex;
                flex-direction: column;
                opacity: 0;
                transform: translateY(10px);
                animation: fadeInUp 0.4s ease forwards;
            }}
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .chat-message.user {{
                background-color: #2b313e;
            }}
            .chat-message.assistant {{
                background-color: #475063;
            }}
            .chat-message .message-content {{
                display: flex;
                align-items: flex-start;
            }}
            .avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
                margin-right: 1rem;
            }}
            .text {{
                line-height: 1.5;
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="chat-container" id="chat-box">
            {chat_html}
        </div>
        <script>
            // ✅ Auto scroll mượt về cuối khi render lại
            const chatBox = document.getElementById('chat-box');
            if (chatBox) {{
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}
        </script>
    </body>
    </html>
    """

    # Dùng components.html để chạy JS + CSS động
    components.html(full_html, height=500, scrolling=False)


@st.dialog("Xác nhận đăng xuất")
def confirm_logout(controller):
    st.write("Bạn có chắc muốn đăng xuất không?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Đăng xuất"):
            st.query_params.page = "login"
            logout(controller)
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

def home_page(controller, access_token_user):   
    #username = get_username_by_id(access_token_user)  
    username = "Người dùng"
    agent_url = get_agent_url()
    if "agent_client" not in st.session_state: 
        try:
            with st.spinner("Đang tải trang..."):
                st.session_state.agent_client = AgentClient(base_url=agent_url)
        except AgentClientError as e:
            st.error(f"Error connecting to agent service at {agent_url}: {e}")
            st.markdown("The service might be booting up. Try again in a few seconds.")
            st.stop()
    agent_client: AgentClient = st.session_state.agent_client
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = str(uuid.uuid4())
            messages = []
        else:
            try:
                messages: ChatHistory = agent_client.get_history(thread_id=thread_id).messages
            except AgentClientError:
                st.error("No message history found for this Thread ID.")
                messages = []
        st.session_state.messages = messages
        st.session_state.thread_id = thread_id

    # Sidebar
    with st.sidebar:
        st.session_state.show_confirm_logout = False
        st.header(f"{APP_ICON} {APP_TITLE}")
        col1, col2 = st.columns([1, 1])  # Chia 2 cột: 3 phần text, 1 phần nút

        with col1:
            st.write(f"Welcome, {username}! 👋")

        with col2:
            if st.button(":material/logout: Logout", use_container_width=True):
                confirm_logout(controller)
        st.write("Let me be your AI assistant and help you with any questions")
        if st.button(":material/chat: New Chat", use_container_width=True):
            try:
                st.write("Creating a new chat session...")
            except Exception as e:
                st.error(f"Error creating new chat session: {str(e)}")
                return

        st.subheader("Chat History")
        #sessions = get_user_chat_sessions(user_id)
        if True:
            chat_sessions = [f"💬 Chat session #{i+1}" for i in range(30)]

            html = r"""
            <div style="
                height: 250px;
                overflow-y: auto;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 4px 8px;
                margin-bottom: 10px;
            ">
            """

            for chat in chat_sessions:
                html += f"""
            <div style="
                padding: 6px 8px;
                margin-bottom: 4px;
                background-color: rgb(142 138 140 / 44%);
                border-radius: 6px;
                cursor: pointer;
            ">
                {chat}
            </div>
            """
            html += "</div>"

            # Dùng markdown
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.write("No previous chats")
        with st.popover(":material/policy: Privacy", use_container_width=True):
            st.write(
                "Your privacy is important to us. Chat data is only used to improve the service and is never shared with third parties."
            )
    #end sidebar
    # message main content
    messages: list[ChatMessage] = st.session_state.messages
    display_messages(messages)
    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([8, 1])  # chia tỷ lệ cột (ô nhập : nút gửi)
        with cols[0]:
            user_input = st.text_input(
                "Câu hỏi của bạn:",
                key="user_input",
                placeholder="Nhập tin nhắn...",
                label_visibility="collapsed",  # ẩn nhãn để gọn
            )
        with cols[1]:
            submitted = st.form_submit_button("📨 Gửi")
    if submitted and user_input:
        send_message(messages, user_input)
        st.rerun()  # bắt buộc rerun lại để hiển thị tin mới
            
    
