import requests
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit.components.v1 as components
import markdown

from utils.helper_link import group_last
from api_call import logout, get_username_by_id, send_message, get_agent_url, get_user_chat_sessions, get_chat_messages
from service.agent_service.clientAgent_service import AgentClient, AgentClientError
from schema.schema import ChatHistory, ChatMessage
from page.order_user import order_user_page
APP_TITLE = "Trợ lý AI tư vấn"
APP_ICON = "🤖"
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

async def display_messages(messages):
    st.markdown("""
    <style>
    /* Target chính xác container chính */
    div[data-testid="stMainBlockContainer"] 
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
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
    if len(messages) == 0:
        messages.append(ChatMessage(type="ai", content="Tôi sẵn lòng giúp đỡ bạn"))
    # print("==============")
    # print(messages)
    for i, message in enumerate(messages):
        role = message.type
        content = message.content
        content = message.content

        if not any(keyword in content for keyword in ["bảng", "so sánh"]):
            clean_content = content.replace("\n\n", "\n")
        else:
            clean_content = content
        #content_clean = normalize_markdown(content)
        #print("Message content:", clean_content)
        html_content = markdown.markdown(
        clean_content,
        extensions=["extra", "tables", "fenced_code"]
        )
        avatar_url = (
            "https://api.dicebear.com/7.x/bottts/svg?seed=assistant"
            if role == "ai"
            else "https://api.dicebear.com/7.x/personas/svg?seed=user"
        )
        chat_html += f"""
        <div class="chat-message {role}">
            <div class="message-content">
                <img class="avatar" src="{avatar_url}">
                <div class="text markdown-body">{html_content}</div>
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
            .chat-message.human {{
                background-color: #2b313e;
            }}
            .chat-message.ai {{
                background-color: #475063;
            }}
            .chat-message .text {{
                white-space: pre-line; 
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
            st.session_state.is_logging_out = True
            st.session_state.checked_cookie = False
            #st.rerun() 
            st.success("Đã đăng xuất, ấn F5 để tiếp tục.")
            st.stop()
            
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

async def home_page(controller, access_token_user):
    try:   
        username = get_username_by_id(access_token_user)[0]
        user_id = get_username_by_id(access_token_user)[1]
    except Exception:
        st.error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
        st.stop()
    agent_url = get_agent_url()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "visible_chat_count" not in st.session_state:
        st.session_state.visible_chat_count = 5
    # if "rewrite_ai" not in st.session_state:
    #     st.session_state.rewrite_ai = OpenAI(api_key=OPENAI_KEY)
    if "agent_client" not in st.session_state: 
        try:
            with st.spinner("Đang tải trang..."):
                st.session_state.agent_client = AgentClient(base_url=agent_url)
                # print("AgentClient type10:", type(st.session_state.agent_client))
        except AgentClientError as e:
            st.error(f"Error connecting to agent service at {agent_url}: {e}")
            st.markdown("The service might be booting up. Try again in a few seconds.")
            st.stop()
    #print("hello")
    agent_client = st.session_state.agent_client
    # rewrite_ai = st.session_state.rewrite_ai
    # print("AgentClient type59:", type(agent_client))
    # print("Has ainvoke:", hasattr(agent_client, "ainvoke"))
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = ""
            #thread_id = str(uuid.uuid4())
            messages = []
        else:
            try:
                messages = get_chat_messages(thread_id)
                #messages: ChatHistory = agent_client.get_history(thread_id=thread_id).messages
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
            st.write(f"Xin chào, {username}! 😊")

        with col2:
            if st.button(":material/logout: logout", use_container_width=True):
                confirm_logout(controller)
        st.write("Thông tin được AI hỗ trợ chỉ mang tính chất tham khảo")
        if st.button(":material/chat: Đoạn chat mới", use_container_width=True):
            try:
                # Create new chat session in database
                session_response = requests.post(
                    f"{get_agent_url()}/messages/chat-sessions",
                    json={"user_id": user_id},
                    verify=False
                )
                session_response.raise_for_status()
                new_session_id = session_response.json()["id"]
                # Update session state
                st.session_state.messages = []
                st.session_state.thread_id = new_session_id
                st.rerun()
            except Exception as e:
                st.error(f"Error creating new chat session: {str(e)}")
                return

        st.subheader("Các đoạn chat của bạn")
        sessions = get_user_chat_sessions(user_id)
        if sessions:
            visible_sessions = list(
    reversed(sessions[-st.session_state.visible_chat_count:])
)

            for chat in visible_sessions:
                label = f"💬 Chat ID: {str(chat['id'])[:8]}"
                if chat["id"] == st.session_state.thread_id:
                    label = "👉 " + label

                if st.button(label, key=f"chat_{chat['id']}"):
                    st.session_state.thread_id = str(chat['id'])
                    # Load messages for this session
                    messages = get_chat_messages(str(chat['id']))
                    st.session_state.messages = messages
                    st.rerun()
            if st.session_state.visible_chat_count < len(sessions):
                if st.button("⬇️ Hiển thị thêm"):
                    st.session_state.visible_chat_count += 5
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write("Chưa có cuộc trò chuyện nào trước đây")
        if st.button(":material/shopping_cart: Giỏ Hàng", use_container_width=True):
            st.query_params.page = "order_user"
            await order_user_page(controller, access_token_user)
            st.rerun()
        with st.popover(":material/policy: Chính sách", use_container_width=True):
            st.write(
                "Quyền riêng tư của bạn rất quan trọng đối với chúng tôi. Dữ liệu trò chuyện chỉ được sử dụng để cải thiện dịch vụ và không bao giờ được chia sẻ với bên thứ ba."
            )
        st.caption(
            "Made with :material/favorite: by QuocHieu in VietNam"
        )
    #end sidebar
    # message main content
    messages: list[ChatMessage] = st.session_state.messages
    #print("current messages:", messages)
    await display_messages(messages)
    if "loading" not in st.session_state:
        st.session_state.loading = False
    if "pending_input" not in st.session_state:
        st.session_state.pending_input = ""
    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([8, 1])  # chia tỷ lệ cột (ô nhập : nút gửi)
        with cols[0]:
            user_input = st.text_input(
                "Câu hỏi của bạn:",
                key="user_input",
                placeholder="Nhập tin nhắn...",
                label_visibility="collapsed",  # ẩn nhãn để gọn
                disabled=st.session_state.loading
            )
        with cols[1]:
            submitted = st.form_submit_button("📨 Gửi", disabled=st.session_state.loading)

    if submitted and user_input:
        st.session_state.historychat = group_last(messages)
        #print("history chat lúc gửi:", st.session_state.thread_id)
        # Create new chat session in database
        if not st.session_state.thread_id or st.session_state.thread_id == "":
            session_response = requests.post(
                f"{get_agent_url()}/messages/chat-sessions",
                json={"user_id": user_id},
                verify=False
            )
            session_response.raise_for_status()
            st.session_state.thread_id = session_response.json()["id"]
            #print("Tạo mới thread_id:", st.session_state.thread_id)
        # Store user message in database
        #print("Gửi message với thread_id:")
        user_message_response = requests.post(
                f"{get_agent_url()}/messages/messages",
                json={
                    "chat_session_id": str(st.session_state.thread_id),
                    "sender_id": user_id,
                    "content": user_input
                },
                verify=False
            )
        if user_message_response.status_code != 200:
                st.error(f"Error storing user message: {user_message_response.text}")
                return
        st.session_state.messages.append(ChatMessage(type="human", content=user_input))
        st.session_state.pending_input = user_input
        st.session_state.loading = True
        
        st.rerun() 

    if st.session_state.loading:
        #user_id = "aaf7ac48-c2a3-4928-98e6-bf9c22b1282c"  # Placeholder user ID
        with st.spinner("Đang tạo ra câu trả lời..."):
            try:
                # print("Input người dùng:", st.session_state.user_input)
                # rewrite_message = rewrite_ai.chat.completions.create(
                #     model="gpt-5-nano", 
                #     messages=[
                #         {"role": "system", "content": "Bạn là bộ tiền xử lý câu hỏi cho hệ thống AI tư vấn bán điện thoại. Bạn chỉ có nhiệm vụ viết lại câu hỏi theo yêu cầu."},
                #         {"role": "user", "content": rewrite_prompt(st.session_state.historychat, st.session_state.user_input)}
                #     ],
                   
                #     )
                # input_rewrite = rewrite_message.choices[0].message.content.strip()
                # print("history chat:", st.session_state.historychat)
                # print("input_rewrite là", input_rewrite)
                response = await agent_client.ainvoke(
                    message=st.session_state.pending_input,
                    thread_id=st.session_state.thread_id,
                    user_id=user_id,
                )
                #print("câu trả lời:", response)
                # Store AI message in database
                ai_message_response = requests.post(
                    f"{get_agent_url()}/messages/ai-messages",
                    json={
                        "chat_session_id": str(st.session_state.thread_id),
                        "content": response.content
                    },
                    verify=False
                )
                if ai_message_response.status_code != 200:
                    st.error(f"Error storing AI message: {ai_message_response.text}")
                    return
                messages.append(response)
                st.session_state.loading = False
                st.rerun()  
            except AgentClientError as e:
                st.session_state.loading = False
                st.error(f"Error generating response: {e}")
                st.stop()
            
    
