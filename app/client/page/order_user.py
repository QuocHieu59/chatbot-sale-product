import requests
import streamlit as st

from api_call import logout, get_username_by_id, get_agent_url

APP_TITLE = "Trợ lý AI tư vấn"
APP_ICON = "🤖"


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

@st.dialog("Cập nhật đơn hàng")
def confirm_update_order(order_id, username, customer_phone, customer_address):
    st.write("Bạn có chắc cập nhật đơn hàng này không?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Cập nhật"):
            res = requests.put(f"{get_agent_url()}/orders/update", json={
                            "order_id": order_id,
                            "username": username,
                            "customer_phone": customer_phone,
                            "customer_address": customer_address
                        }, verify=False)
            if res.status_code == 200:
                st.success("Đơn hàng đã được cập nhật!")
            else:
                st.error("Cập nhật đơn hàng thất bại!")
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

@st.dialog("Xác nhận xóa đơn hàng")
def confirm_delete_order(order_id):
    st.write("Bạn có chắc muốn xóa đơn hàng này không?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Xóa"):
            res = requests.delete(f"{get_agent_url()}/orders/delete", json={"order_id": order_id}, verify=False)
            if res.status_code == 200:
                st.success("Đơn hàng đã được xóa!")
            else:
                st.error("Xóa đơn hàng thất bại!")
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

async def order_user_page(controller, access_token_user):  
    username = get_username_by_id(access_token_user)[0]
    user_id = get_username_by_id(access_token_user)[1]
    # print("User ID in order_user_page:", user_id)
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = ""
            #thread_id = str(uuid.uuid4())
        st.session_state.thread_id = thread_id

    # Sidebar
    with st.sidebar:
        st.session_state.show_confirm_logout = False
        st.header(f"{APP_ICON} {APP_TITLE}")
        col1, col2 = st.columns([1, 1])  # Chia 2 cột: 3 phần text, 1 phần nút

        with col1:
            st.write(f"Xin chào, {username}! 😊")
        with col2:
            if st.button(":material/logout: logout",key="logout_button", use_container_width=True):
                confirm_logout(controller)
        st.write("Thông tin được AI hỗ trợ chỉ mang tính chất tham khảo")
        if st.button(":material/home: Quay lại", key="back_button", use_container_width=True):
            st.query_params.page = "home"
            st.rerun()
        with st.popover(":material/policy: Chính sách", use_container_width=True):
            st.write(
                "Quyền riêng tư của bạn rất quan trọng đối với chúng tôi. Dữ liệu trò chuyện chỉ được sử dụng để cải thiện dịch vụ và không bao giờ được chia sẻ với bên thứ ba."
            )
        st.caption(
            "Made with :material/favorite: by QuocHieu in VietNam"
        )
    #end sidebar
    # order main content
    # ================= ORDER MAIN CONTENT =================
    st.markdown(
        """
        <style>
        /* Chỉ chỉnh main content, KHÔNG ảnh hưởng sidebar */
        div[data-testid="stMainBlockContainer"] {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 1400px !important;  /* tăng chiều ngang bảng */
        }
        
        /* Main content */
        section[data-testid="stMain"] 
        div[data-testid="stVerticalBlock"] {
            gap: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    res = requests.get(f"{get_agent_url()}/orders/list", json={"id_user": user_id}, verify=False)
    result = res.json()
    # print("Order API result:", result)
    if result["success"]:
        order_list = result["data"] 
    else:
        order_list = []
    st.title("📦 Đơn hàng của bạn")

    # --- Gọi API lấy danh sách đơn hàng ---
    # Ví dụ API trả về list các dict
    # orders = controller.get_orders_by_user(user_id, access_token_user)
    # <-- tạm thời để trống, bạn thay bằng API thật

    if order_list:
        st.subheader("Danh sách đơn hàng")

        # Header bảng
        header_cols = st.columns([1, 3, 2, 2, 2, 2])
        header_cols[0].markdown("**Mã đơn**")
        header_cols[1].markdown("**Thông tin sản phẩm**")
        header_cols[2].markdown("**Tên**")
        header_cols[3].markdown("**SĐT**")
        header_cols[4].markdown("**Địa chỉ**")
        header_cols[5].markdown("**Tùy chọn**")

        st.divider()

        # Render từng đơn hàng
        for order in order_list:
            cols = st.columns([1, 3, 2, 2, 3, 2])

            cols[0].write(str(order.get("id", ""))[:8])
            cols[1].write(order.get("info", ""))
            username = cols[2].text_input(
                label="",
                value=order.get("username", ""),
                key=f"username_{order['id']}"
                )

            customer_phone = cols[3].text_input(
                label="",
                value=order.get("customer_phone", ""),
                key=f"phone_{order['id']}"
            )

            customer_address = cols[4].text_input(
                label="",
                value=order.get("customer_address", ""),
                key=f"address_{order['id']}",
               
            )

            with cols[5]:
                btn_col1, btn_col2 = st.columns(2)

                with btn_col1:
                    if st.button(
                        ":material/edit:",
                        key=f"update_{order['id']}",
                        help="Cập nhật đơn hàng"
                    ):
                        confirm_update_order(
                            order["id"],
                            username,
                            customer_phone,
                            customer_address
                        )
                    
                with btn_col2:
                    if st.button(
                        ":material/delete:",
                        key=f"delete_{order['id']}",
                        help="Xóa đơn hàng"
                    ):
                        confirm_delete_order(order["id"])
                        #st.session_state.order_action = "delete"
                        

    else:
        st.info("📭 Bạn chưa có đơn hàng nào.")
    
