import requests
import streamlit as st

from api_call import logout, get_username_by_id, get_agent_url

APP_TITLE = "Trợ lý AI tư vấn"
APP_ICON = "🏬"

# ===================== DIALOG =====================

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


@st.dialog("Xác nhận xóa shop")
def confirm_delete_shop(shop_id):
    st.write("Bạn có chắc muốn xóa shop này không?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Xóa"):
            res = requests.delete(
                f"{get_agent_url()}/shop/admin/delete",
                json={"shop_id": shop_id},
                verify=False
            )
            if res.status_code == 200:
                st.success("Shop đã được xóa!")
            else:
                st.error("Xóa shop thất bại!")
            st.rerun()

    with col2:
        if st.button("❌ Hủy"):
            st.rerun()


@st.dialog("Tạo mới shop")
def open_create_shop_dialog():
    st.write("Vui lòng nhập thông tin shop")

    name_shop = st.text_input("Tên shop")
    address = st.text_input("Địa chỉ")
    wrk_hrs = st.text_input("Giờ làm việc")
    link = st.text_input("Link")
    inf_staff = st.text_input("Thông tin nhân viên")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Tạo"):
            if not name_shop or not address or not wrk_hrs or not link or not inf_staff:
                st.warning("Vui lòng nhập đầy đủ thông tin")
                return

            res = requests.post(
                f"{get_agent_url()}/shop/admin/create",
                json={
                    "name_shop": name_shop,
                    "adress": address,
                    "wrk_hrs": wrk_hrs,
                    "link": link,
                    "inf_staff": inf_staff
                },
                verify=False
            )

            if res.status_code == 200:
                st.success("Shop đã được tạo!")
            else:
                st.error("Tạo shop thất bại!")

            st.rerun()
    with col2:
        if st.button("❌ Hủy"):
            st.rerun()


@st.dialog("Cập nhật shop")
def confirm_update_shop(shop_id, name_shop, address, wrk_hrs, link, inf_staff):
    st.write("Bạn có chắc muốn cập nhật shop này không?")
    if (not name_shop) or (not address) or (not wrk_hrs) or (not link) or (not inf_staff):
        st.error("Vui lòng điền đầy đủ thông tin trước khi cập nhật!")
        return
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Cập nhật"):
            res = requests.put(
                f"{get_agent_url()}/shop/admin/update",
                json={
                    "id": shop_id,
                    "name_shop": name_shop,
                    "adress": address,
                    "wrk_hrs": wrk_hrs,
                    "link": link,
                    "inf_staff": inf_staff
                },
                verify=False
            )

            if res.status_code == 200:
                st.success("Shop đã được cập nhật!")
            else:
                st.error("Cập nhật shop thất bại!")

            st.rerun()

    with col2:
        if st.button("❌ Hủy"):
            st.rerun()


# ===================== PAGE =====================

async def admin_shop_page(controller, access_token_user):
    try:
        username = get_username_by_id(access_token_user)[0]
        userrole = get_username_by_id(access_token_user)[2]
    except Exception:
        st.error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
        st.stop()
    if userrole != "admin":
        st.error("Bạn không có quyền truy cập trang này!")
        st.stop()

    # ================= SIDEBAR =================
    with st.sidebar:
        st.header(f"{APP_ICON} {APP_TITLE}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Xin chào, admin {username}! 😊")
        with col2:
            if st.button(":material/logout: logout", use_container_width=True):
                confirm_logout(controller)

        st.write("Thông tin được AI hỗ trợ chỉ mang tính chất tham khảo")

        if st.button(":material/store: Tạo mới shop", use_container_width=True):
            open_create_shop_dialog()

        if st.button(":material/person: Người dùng", use_container_width=True):
            st.query_params.page = "admin"
            st.rerun()

        if st.button(":material/smartphone: Điện thoại", key="btn_phone", use_container_width=True):
            st.query_params.page = "phone"
            
            st.rerun()    

        if st.button(":material/receipt_long: Đơn hàng", use_container_width=True):
            st.query_params.page = "admin_order"
            st.rerun()

        with st.popover(":material/policy: Chính sách", use_container_width=True):
            st.write(
                "Dữ liệu được sử dụng cho mục đích quản trị hệ thống và không chia sẻ cho bên thứ ba."
            )

        st.caption("Made with ❤️ by QuocHieu in VietNam")

    # ================= MAIN STYLE =================
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

    # ================= FETCH SHOP LIST =================
    res = requests.get(f"{get_agent_url()}/shop/admin/list", verify=False)
    result = res.json()

    shop_list = result["data"] if result.get("status") == "success" else []

    st.title("Danh sách shop")

    if shop_list:
        header = st.columns([1, 2, 3, 2, 2, 2, 2])
        header[0].markdown("**ID**")
        header[1].markdown("**Tên shop**")
        header[2].markdown("**Địa chỉ**")
        header[3].markdown("**Giờ làm việc**")
        header[4].markdown("**Link**")
        header[5].markdown("**Thông tin nhân viên**")
        header[6].markdown("**Tùy chọn**")

        st.divider()

        for shop in shop_list:
            cols = st.columns([1, 2, 3, 2, 2, 2, 2])

            cols[0].write(str(shop["id"])[:8])

            name_shop = cols[1].text_input(
                "",
                shop.get("name_shop", ""),
                key=f"name_{shop['id']}"
            )

            address = cols[2].text_input(
                "",
                shop.get("adress", ""),
                key=f"address_{shop['id']}"
            )

            wrk_hrs = cols[3].text_input(
                "",
                shop.get("wrk_hrs", ""),
                key=f"wrk_hrs_{shop['id']}"
            )

            link = cols[4].text_input(
                "",
                shop.get("link", ""),
                key=f"link_{shop['id']}"
            )
            inf_staff = cols[5].text_input(
                "",
                shop.get("inf_staff", ""),
                key=f"inf_staff_{shop['id']}"
            )

            with cols[6]:
                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        ":material/edit:",
                        key=f"update_{shop['id']}",
                        help="Cập nhật shop"
                    ):
                        confirm_update_shop(
                            shop["id"],
                            name_shop,
                            address,
                            wrk_hrs,
                            link,
                            inf_staff
                        )

                with c2:
                    if st.button(
                        ":material/delete:",
                        key=f"delete_{shop['id']}",
                        help="Xóa shop"
                    ):
                        confirm_delete_shop(shop["id"])
    else:
        st.info("🏬 Chưa có shop nào được tạo.")