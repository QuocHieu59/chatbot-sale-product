import requests
import streamlit as st

from api_call import logout, get_username_by_id, get_agent_url
from page.admin_shop import admin_shop_page

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

@st.dialog("Xác nhận xóa người dùng")
def confirm_delete_user(user_id):
    st.write("Bạn có chắc muốn xóa người dùng này không?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Xóa"):
            res = requests.delete(f"{get_agent_url()}/users/admin/delete", json={"user_id": user_id}, verify=False)
            if res.status_code == 200:
                st.success("Người dùng đã được xóa!")
            else:
                st.error("Xóa người dùng thất bại!")
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

@st.dialog("Tạo mới người dùng")
def open_create_user_dialog():
    st.write("Vui lòng nhập thông tin người dùng")

    name = st.text_input("Tên đăng nhập")
    email = st.text_input("Email")
    password = st.text_input("Mật khẩu", type="password")
    role = st.selectbox("Quyền", ["user", "admin"])
    age = st.number_input("Tuổi", min_value=1, max_value=100, step=1)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Tạo"):
            if not name or not email or not password:
                st.warning("Vui lòng nhập đầy đủ thông tin")
                return
            res = requests.post(f"{get_agent_url()}/users/admin/create", json={
                            "name": name,
                            "email": email,
                            "role": role,
                            "age": age,
                            "password": password
                        }, verify=False)
            if res.status_code == 200:
                st.success("Người dùng đã được tạo!")
            else:
                st.error("Tạo người dùng thất bại!")
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

@st.dialog("Cập nhật người dùng")
def confirm_update_user(user_id, name, email, role, age):
    st.write("Bạn có chắc cập nhật người dùng này không?")
    if (not name) or (not email) or (not role) or (not age):
        st.error("Vui lòng điền đầy đủ thông tin trước khi cập nhật!")
        return
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Cập nhật"):
            res = requests.put(f"{get_agent_url()}/users/admin/update", json={
                            "id": user_id,
                            "name": name,
                            "email": email,
                            "role": role,
                            "age": age
                        }, verify=False)
            if res.status_code == 200:
                st.success("Đơn hàng đã được cập nhật!")
            else:
                st.error("Cập nhật đơn hàng thất bại!")
            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()

async def admin_user_page(controller, access_token_user):  
    try:
        username = get_username_by_id(access_token_user)[0]
        userrole = get_username_by_id(access_token_user)[2]
    except Exception:
        st.error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
        st.stop()
    #print("User role in admin_user_page:", userrole)
    if userrole != "admin":
        st.error("Bạn không có quyền truy cập trang này!")
        st.stop()
    # print("User ID in order_user_page:", user_id)
    # Sidebar
    if "show_create_user" not in st.session_state:
        st.session_state.show_create_user = False
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
        if st.button(":material/person_add: Tạo mới người dùng", key="created_user", use_container_width=True):
            open_create_user_dialog()
        if st.button(":material/store: Shop", key="btn_shop",  use_container_width=True):
            st.query_params.page = "shop"
            await admin_shop_page(controller, access_token_user)
            st.rerun()
        if st.button(":material/smartphone: Điện thoại", key="btn_phone", use_container_width=True):
            st.query_params.page = "phone"
            
            st.rerun()
        if st.button(":material/receipt_long: Đơn hàng", key="btn_admin_order",  use_container_width=True):
            st.query_params.page = "admin_order"
            
            st.rerun()
        with st.popover(":material/policy: Chính sách", use_container_width=True):
            st.write(
                "Quyền riêng tư của bạn rất quan trọng đối với chúng tôi. Dữ liệu trò chuyện chỉ được sử dụng để cải thiện dịch vụ và không bao giờ được chia sẻ với bên thứ ba."
            )
        st.caption(
            "Made with :material/favorite: by QuocHieu in VietNam"
        )
    #end sidebar
    # user main content
    # ================= USER MAIN CONTENT =================
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
    res = requests.get(f"{get_agent_url()}/users/admin/list", verify=False)
    result = res.json()
    # print("Order API result:", result)
    if result["status"] == "success":
        user_list = result["data"] 
    else:
        user_list = []
    st.title("Danh sách người dùng")

    # --- Gọi API lấy danh sách người dùng ---

    if user_list:
        # Header bảng
        header_cols = st.columns([1, 3, 3, 2, 1, 2])
        header_cols[0].markdown("**id**")
        header_cols[1].markdown("**email**")
        header_cols[2].markdown("**Tên**")
        header_cols[3].markdown("**Vai trò**")
        header_cols[4].markdown("**Tuổi**")
        header_cols[5].markdown("**Tùy chọn**")

        st.divider()

        # Render từng đơn hàng
        for user in user_list:
            cols = st.columns([1, 3, 3, 2, 1, 2])

            cols[0].write(str(user.get("id", ""))[:8])
            name = cols[1].text_input(
                label="",
                value=user.get("name", ""),
                key=f"name_{user['id']}"
                )

            email = cols[2].text_input(
                label="",
                value=user.get("email", ""),
                key=f"email_{user['id']}"
            )

            role = cols[3].text_input(
                label="",
                value=user.get("role", ""),
                key=f"role_{user['id']}",
               
            )

            age = cols[4].text_input(
                label="",
                value=user.get("age", ""),
                key=f"age_{user['id']}"
            )

            with cols[5]:
                btn_col1, btn_col2 = st.columns(2)

                with btn_col1:
                    if st.button(
                        ":material/edit:",
                        key=f"update_{user['id']}",
                        help="Cập nhật người dùng"
                    ):
                        confirm_update_user(
                            user["id"],
                            name,
                            email,
                            role,
                            age
                        )
                    
                with btn_col2:
                    if st.button(
                        ":material/delete:",
                        key=f"delete_{user['id']}",
                        help="Xóa người dùng"
                    ):
                        confirm_delete_user(user["id"])
                        #st.session_state.order_action = "delete"
                        
    
