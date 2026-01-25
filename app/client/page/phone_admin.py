import requests
import streamlit as st
import pandas as pd

from api_call import logout, get_username_by_id, get_agent_url

APP_TITLE = "Trợ lý AI tư vấn"
APP_ICON = "🏬"

# ===================== DIALOG =====================

@st.dialog("Xác nhận đăng xuất")
def confirm_logout(controller):
    st.write("Bạn có chắc muốn đăng xuất không?")
    
    if st.button("✅ Đăng xuất"):
            st.query_params.page = "login"
            logout(controller)
            st.session_state.is_logging_out = True
            st.session_state.checked_cookie = False
            #st.rerun() 
            st.success("Đã đăng xuất, ấn F5 để tiếp tục.")
            st.stop()
    if st.button("❌ Hủy"):
            st.rerun()


@st.dialog("Xác nhận xóa điện thoại")
def confirm_delete_phone(phone_id):
    st.write("Bạn có chắc muốn xóa điện thoại này không?")

    if st.button("✅ Xóa"):
            res = requests.delete(
                f"{get_agent_url()}/phone/admin/delete",
                json={"phone_id": phone_id},
                verify=False
            )
            if res.status_code == 200:
                st.success("Điện thoại đã được xóa!")
                st.session_state.need_reload = True
            else:
                st.error("Xóa điện thoại thất bại!")
            #st.rerun()


    if st.button("❌ Hủy"):
            st.rerun()


@st.dialog("Tạo mới điện thoại")
def open_create_phone_dialog():
    st.write("Vui lòng nhập thông tin điện thoại")

    name = st.text_input("Tên điện thoại")
    current_price = st.number_input("Giá", min_value=0.0)

    color_options = st.text_input("Màu sắc")
    network_sp = st.number_input("Mạng (4G/5G = 4/5)", min_value=0, step=1)
    charge_tech = st.number_input("Công nghệ sạc (W)", min_value=0, step=1)
    screen_size = st.text_input("Kích thước màn hình")
    ram = st.text_input("RAM")
    os = st.text_input("Hệ điều hành")
    chip = st.text_input("Chip")
    memory = st.text_input("Bộ nhớ")
    pin = st.number_input("Pin (mAh)", min_value=1)

    sale = st.number_input("Giảm giá (%)", min_value=0.0, max_value=100.0, step=1.0)
    status = st.checkbox("Đang bán", value=True)
    phone_company = st.text_input("Hãng")




    if st.button("✅ Tạo"):
            if not all([
                name, current_price, color_options, screen_size, ram,
                os, chip, memory, pin, phone_company
            ]):
                st.warning("Vui lòng nhập đầy đủ thông tin bắt buộc")
                return

            res = requests.post(
                f"{get_agent_url()}/product/create",
                json={
                    "name": name,
                    "current_price": current_price,
                    "color_options": color_options,
                    "network_sp": network_sp,
                    "charge_tech": charge_tech,
                    "screen_size": screen_size,
                    "ram": ram,
                    "os": os,
                    "chip": chip,
                    "memory": memory,
                    "pin": pin,
                    "sale": sale,
                    "status": status,
                    "phone_company": phone_company,
                    
                },
                verify=False
            )

            if res.status_code == 200:
                st.success("Điện thoại đã được tạo!")
                st.session_state.need_reload = True
            else:
                st.error(f"Tạo điện thoại thất bại! {res.text}")

            #st.rerun()

    if st.button("❌ Hủy"):
            st.rerun()



@st.dialog("Cập nhật điện thoại")
def confirm_update_phone(
    phone_id,
    name,
    current_price,
    color_options,
    network_sp,
    charge_tech,
    screen_size,
    ram,
    os,
    chip,
    memory,
    pin,
    phone_company,
    sale,
    status,
):
    st.write("Bạn có chắc muốn cập nhật điện thoại này không?")


    if st.button("✅ Cập nhật"):
            res = requests.put(
                f"{get_agent_url()}/product/update",
                json={
                    "product_id": phone_id,
                    "name": name,
                    "current_price": current_price,
                    "color_options": color_options,
                    "network_sp": network_sp,
                    "charge_tech": charge_tech,
                    "screen_size": screen_size,
                    "ram": ram,
                    "os": os,
                    "chip": chip,
                    "memory": memory,
                    "pin": pin,
                    "sale": sale,
                    "status": status,
                    "phone_company": phone_company,
                },
                verify=False
            )

            if res.status_code == 200:
                st.success("Điện thoại đã được cập nhật!")
                st.session_state.need_reload = True
            else:
                st.error(f"Cập nhật điện thoại thất bại! {res.text}")

            #st.rerun()

    if st.button("❌ Hủy"):
            st.rerun()


# ===================== PAGE =====================

async def admin_phone_page(controller, access_token_user):
    username = get_username_by_id(access_token_user)[0]
    userrole = get_username_by_id(access_token_user)[2]
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

        if st.button(":material/store: Tạo mới điện thoại", use_container_width=True):
            open_create_phone_dialog()

        if st.button(":material/person: Người dùng", use_container_width=True):
            st.query_params.page = "admin"
            st.rerun()

        if st.button(":material/store: Shop", key="btn_shop",  use_container_width=True):
            st.query_params.page = "shop"
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
        /* Fix container nút trong column "Tùy chọn" */
        .st-emotion-cache-4rsbii {
            display: block !important;
            padding-left: 2rem !important;
            padding-bottom: 3rem !important;
            justify-content: flex-start !important;
            gap: 0.4rem !important;
            width: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <style>
        /* Chỉ chỉnh main content, KHÔNG ảnh hưởng sidebar */
        div[data-testid="stMainBlockContainer"] {
            padding-left: 0.1rem !important;
            padding-right: 0.1rem !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
              /* tăng chiều ngang bảng */
        }
        
        /* Main content */
        section[data-testid="stMain"] 
        div[data-testid="stVerticalBlock"] {
            gap: 0.25rem;
        }
         /* Ép main container cho phép cuộn ngang */
        section[data-testid="stMain"] {
            overflow-x: auto !important;
        }

        /* Cho bảng không bị wrap */
        div[data-testid="stHorizontalBlock"] {
            min-width: 2000px; /* tăng nếu bảng còn tràn */
        }

        /* Giữ cell không xuống dòng */
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stText"] {
            white-space: nowrap !important;
        }
        section[data-testid="stSidebar"] 
        div[data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] 
        div[data-testid="stText"] {
            white-space: normal !important;
            overflow-wrap: break-word !important;
            word-break: break-word !important;
        }

        /* Không ép rộng sidebar */
        section[data-testid="stSidebar"] 
        div[data-testid="stHorizontalBlock"] {
            min-width: unset !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ================= FETCH PHONE LIST =================
    if "page" not in st.session_state:
        st.session_state.page = 0

    if "page_size" not in st.session_state:
        st.session_state.page_size = 20

    if "phones" not in st.session_state:
        st.session_state.phones = []
    if "last_loaded_page" not in st.session_state:
        st.session_state.last_loaded_page = -1
    params = {
        "page": st.session_state.page,
        "size": st.session_state.page_size
    }
     # ====== RELOAD SAU UPDATE / DELETE ======
    if "need_reload" not in st.session_state:
            st.session_state.need_reload = False

    if st.session_state.need_reload:
            st.session_state.need_reload = False
            st.session_state.phones = []
            st.session_state.page = 0
            st.session_state.last_loaded_page = -1
            st.rerun()

    res = requests.get(f"{get_agent_url()}/product/all",params=params, verify=False)
    result = res.json()

    # ---------- LIMIT STATE ----------
    if "phone_limit" not in st.session_state:
        st.session_state.phone_limit = 20

    if result.get("success") is True:
        data = result["data"]
        new_phones = data["content"]   # Spring Page.content
        last_page = data["last"]
        if st.session_state.page != st.session_state.last_loaded_page:
            st.session_state.phones.extend(new_phones)
            st.session_state.last_loaded_page = st.session_state.page
    st.title("Danh sách điện thoại")

    if st.session_state.phones:
        visible_phones = st.session_state.phones

        # ---------- SCROLL CONTAINER ----------
        st.markdown(
        '<div style="overflow-x: auto; white-space: nowrap;">',
        unsafe_allow_html=True
    )
        col_widths = [
            1,    # STT
            1.5,  # ID
            3,    # Tên
            2.5,  # Giá
            2.5,    # Màu
            1.2,    # Mạng
            1.5,    # Sạc
            1.5,  # Màn hình
            1.5,    # RAM
            2,    # OS
            2.5,  # Chip
            1.6,  # Bộ nhớ
            2,    # Pin
            1.6,  # Hãng
            1.5,  # Sale
            1,  # Status
            1.2   # Tùy chọn
        ]
        header = st.columns(col_widths)
        header[0].markdown("**STT**")
        header[1].markdown("**ID**")
        header[2].markdown("**Tên**")
        header[3].markdown("**Giá**")
        header[4].markdown("**Màu**")
        header[5].markdown("**Mạng**")
        header[6].markdown("**Sạc**")
        header[7].markdown("**Màn hình**")
        header[8].markdown("**RAM**")
        header[9].markdown("**OS**")
        header[10].markdown("**Chip**")
        header[11].markdown("**Bộ nhớ**")
        header[12].markdown("**Pin**")
        header[13].markdown("**Hãng**")
        header[14].markdown("**Sale**")
        header[15].markdown("**Status**")
        header[16].markdown("**Tùy chọn**")

        st.divider()

        for idx, phone in enumerate(st.session_state.phones, start=1):
            cols = st.columns(col_widths)

            cols[0].write(str(idx))

            cols[1].write(str(phone["id"])[:8])

            name = cols[2].text_input(
                "",
                phone.get("name", ""),
                key=f"name_{phone['id']}_{idx}"
            )

            price = cols[3].number_input(
                "",
                value=float(phone.get("current_price", 0)),
                key=f"price_{phone['id']}_{idx}"
            )

            color = cols[4].text_input(
                "",
                phone.get("color_options", ""),
                key=f"color_{phone['id']}_{idx}"
            )

            network_sp = cols[5].number_input(
                "",
                value=int(phone.get("network_sp", 0)),
                key=f"network_{phone['id']}_{idx}"
            )

            charge_tech = cols[6].number_input(
                "",
                value=int(phone.get("charge_tech", 0)),
                key=f"charge_{phone['id']}_{idx}"
            )

            screen_size = cols[7].text_input(
                "",
                phone.get("screen_size", ""),
                key=f"screen_{phone['id']}_{idx}"
            )

            ram = cols[8].text_input(
                "",
                phone.get("ram", ""),
                key=f"ram_{phone['id']}_{idx}"
            )

            os = cols[9].text_input(
                "",
                phone.get("os", ""),
                key=f"os_{phone['id']}_{idx}"
            )

            chip = cols[10].text_input(
                "",
                phone.get("chip", ""),
                key=f"chip_{phone['id']}_{idx}"
            )

            memory = cols[11].text_input(
                "",
                phone.get("memory", ""),
                key=f"memory_{phone['id']}_{idx}"
            )

            pin = cols[12].number_input(
                "",
                value=int(phone.get("pin", 0)),
                key=f"pin_{phone['id']}_{idx}"
            )

            company = cols[13].text_input(
                "",
                phone.get("phone_company", ""),
                key=f"company_{phone['id']}_{idx}"
            )

            sale = cols[14].number_input(
                "",
                value=float(phone.get("sale", 0)),
                key=f"sale_{phone['id']}_{idx}"
            )

            status = cols[15].checkbox(
                "",
                value=bool(phone.get("status", True)),
                key=f"status_{phone['id']}_{idx}"
            )

            with cols[16]:
                st.markdown(
                '<div style="display: flex; gap: 0.4rem; justify-content: flex-start;">',
                unsafe_allow_html=True
            )


                if st.button(
                        ":material/edit:",
                        key=f"update_{phone['id']}_{idx}",
                        help="Cập nhật điện thoại"
                    ):
                    confirm_update_phone(
                            phone["id"],
                            name,
                            price,
                            color,
                            network_sp,
                            charge_tech,
                            screen_size,
                            ram,
                            os,
                            chip,
                            memory,
                            pin,
                            company,
                            sale,
                            status,
                        )

                if st.button(
                        ":material/delete:",
                        key=f"delete_{phone['id']}_{idx}",
                        help="Xóa điện thoại"
                    ):
                    confirm_delete_phone(phone["id"])
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- LOAD MORE ----------
        if not last_page:
            if st.button("Xem thêm"):
                st.session_state.page += 1
                st.rerun()
       
    else:
        st.info("🏬 Chưa có điện thoại nào được tạo.")