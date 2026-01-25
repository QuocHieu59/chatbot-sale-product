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
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

@st.dialog("Tạo mới đơn hàng")
def open_create_order_dialog():
    st.write("Vui lòng nhập thông tin đơn hàng")

    id_phone = st.text_input("id điện thoại")
    id_user = st.text_input("id người mua")
    customer_phone = st.text_input("SĐT")
    customer_address = st.text_input("Địa chỉ")
    color = st.text_input("Màu")
    info = st.text_input("Thông tin điện thoại")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Tạo"):
            if not id_phone or not id_user or not customer_phone or not customer_address or not color or not info:
                st.warning("Vui lòng nhập đầy đủ thông tin")
                return
            res = requests.post(f"{get_agent_url()}/orders", json={
                            "id_phone": id_phone,
                            "id_user": id_user,
                            "customer_phone": customer_phone,
                            "customer_address": customer_address,
                            "color": color,
                            "info": info
                        }, verify=False)
            if res.status_code == 200:
                st.success("Đơn hàng đã được tạo!")
            else:
                st.error("Tạo đơn hàng thất bại!")
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()


@st.dialog("Cập nhật đơn hàng")
def confirm_update_order(order_id, username, customer_phone, customer_address, info):
    st.write("Bạn có chắc cập nhật đơn hàng này không?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Cập nhật"):
            res = requests.put(f"{get_agent_url()}/orders/update", json={
                            "order_id": order_id,
                            "username": username,
                            "customer_phone": customer_phone,
                            "customer_address": customer_address,
                            "info": info
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

async def order_admin_page(controller, access_token_user):  
    username = get_username_by_id(access_token_user)[0]

    # Sidebar
    with st.sidebar:
        st.session_state.show_confirm_logout = False
        st.header(f"{APP_ICON} {APP_TITLE}")
        col1, col2 = st.columns([1, 1])  # Chia 2 cột: 3 phần text, 1 phần nút

        with col1:
            st.write(f"Xin chào, admin {username}! 😊")
        with col2:
            if st.button(":material/logout: logout",key="logout_button", use_container_width=True):
                confirm_logout(controller)
        st.write("Thông tin được AI hỗ trợ chỉ mang tính chất tham khảo")
        if st.button(":material/add_shopping_cart: Tạo mới đơn hàng", key="created_order", use_container_width=True):
            open_create_order_dialog()
           
        if st.button(":material/store: Shop", key="btn_shop",  use_container_width=True):
            st.query_params.page = "shop"

            st.rerun()
        if st.button(":material/smartphone: Điện thoại", key="btn_phone", use_container_width=True):
            st.query_params.page = "phone"
            
            st.rerun()
        if st.button(":material/person: Người dùng", key="user_btn",  use_container_width=True):
            st.query_params.page = "admin"
            
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
    res = requests.get(f"{get_agent_url()}/orders/all", verify=False)
    result = res.json()
    #print("Order API result:", result)
    if result["success"]:
        order_list = result["data"] 
    else:
        order_list = []
    st.title("📦 Đơn hàng hệ thống")

    # --- Gọi API lấy danh sách đơn hàng ---
    # Ví dụ API trả về list các dict
    # orders = controller.get_orders_by_user(user_id, access_token_user)
    # <-- tạm thời để trống, bạn thay bằng API thật

    if order_list:
        st.subheader("Danh sách đơn hàng")

        # Header bảng
        header_cols = st.columns([1, 2, 2, 2, 3, 2])
        header_cols[0].markdown("**Mã đơn**")
        header_cols[1].markdown("**Tên**")
        header_cols[2].markdown("**SĐT**")
        header_cols[3].markdown("**Địa chỉ**")
        header_cols[4].markdown("**Thông tin sản phẩm**")
        header_cols[5].markdown("**Tùy chọn**")

        st.divider()

        # Render từng đơn hàng
        for order in order_list:
            cols = st.columns([1, 2, 2, 2, 3, 2])

            cols[0].write(str(order.get("id", ""))[:8])
            username = cols[1].text_input(
                label="",
                value=order.get("username", ""),
                key=f"username_{order['id']}"
                )

            customer_phone = cols[2].text_input(
                label="",
                value=order.get("customer_phone", ""),
                key=f"phone_{order['id']}"
            )

            customer_address = cols[3].text_input(
                label="",
                value=order.get("customer_address", ""),
                key=f"address_{order['id']}",
               
            )
            info = cols[4].text_input(
                label="",
                value=order.get("info", ""),
                key=f"info{order['id']}",
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
                            customer_address,
                            info
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
        st.info("📭 Chưa có đơn hàng nào.")
    
