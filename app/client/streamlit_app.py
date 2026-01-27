from pathlib import Path
import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logging
import asyncio
from PIL import Image
from streamlit_cookies_controller import CookieController

from page.admin import admin_user_page
from page.login import login_page
from page.register import register_page
from page.home import home_page
from page.order_user import order_user_page
from api_call import refresh_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS 

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "public" / "mobile-shopping.png"
APP_TITLE = "Goluck Store"
APP_ICON = Image.open(ICON_PATH)

logger = logging.getLogger(__name__)

async def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        menu_items={},
    )
    st.markdown("""
    <style>
    /* Đặt tiêu đề custom lên header mặc định */
    header[data-testid="stHeader"]::after {
        content: "Goluck Store Xin Chào Quý Khách!👋";
        position: absolute;
        font-size: 1.5rem;
        font-weight: 400;
        color: Black;
    }

/* Tuỳ chọn style cho header */
    header[data-testid="stHeader"] {
        background: #f9f9f9;
        display: flex;
        align-items: center;
        height: 3.5rem;
        position: relative;
        justify-content: center;
        z-index: 999;
        border-bottom: 1px solid #ccc;
    }
        /* Ẩn nút Deploy */
    div[data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* Ẩn menu ba chấm (Main Menu) */
    #MainMenu, [data-testid="stMainMenu"] {
        display: none !important;
    }

    /* (Tuỳ chọn) Ẩn cả "Made with Streamlit" ở footer nếu muốn */
    footer {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    if "is_logging_out" not in st.session_state:
        st.session_state.is_logging_out = False

    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        #await asyncio.sleep(0.1)
        #st.rerun()
    if "checked_cookie" not in st.session_state:
        st.session_state.checked_cookie = False
    
    if st.session_state.get("is_logging_out"):
        st.query_params.page = "login"
        st.session_state.checked_cookie = False
        st.session_state.is_logging_out = False
        st.stop()

    controller = CookieController()
    
    access_token_user = controller.get('access_token_user')
    refresh_access_user = controller.get('refresh_token_user')
    is_logging_out = st.session_state.get("is_logging_out", False)
    #print("Access token from cookie:", access_token_user)
    #print("Refresh token from cookie:", refresh_access_user)
    # if not st.session_state.checked_cookie:
    #     if access_token_user is None and refresh_access_user is None:
    #         st.session_state.checked_cookie = True
    #         st.stop()   # ⛔ dừng run đầu tiên
    #     st.session_state.checked_cookie = True
    if access_token_user is None and refresh_access_user is None:
        params = st.query_params
        current_page = params.get("page", "login")
        if current_page == "register":
            register_page()
        else:
            #print("No tokens found, redirecting to login page.")
            login_page(controller)

        return
    elif access_token_user is None and refresh_access_user is not None:
        #print("No access token, but refresh token found. Attempting to refresh...")
        if not refresh_access_token(refresh_access_user, controller):
            st.info("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.")
        #print("Cookie found:", usernameCookie)
            return
        else:
            if not is_logging_out:
                controller.set('access_token_user', access_token_user, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, path='/')
    else:
        if not is_logging_out:
            #print("Setting cookies again to extend expiry.")
            controller.set('access_token_user', access_token_user, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 4, path='/')
            controller.set('refresh_token_user', refresh_access_user, max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, path='/')
            # controller.remove('access_token_user', path='/')
            # controller.remove('refresh_token_user', path='/')
            # print("Cookies after resetting:")
            # print("access_token_user:", controller.get('access_token_user'))
    params = st.query_params

    current_page = params.get("page", "login")
    # print("Access token valid:", controller.get('access_token_user'))
    # print("Current page:", current_page)
    if current_page == "login":
        login_page(controller)
    elif current_page == "register":
        register_page()
    elif current_page == "home":
        await home_page(controller, access_token_user)
    elif current_page == "order_user":
        await order_user_page(controller, access_token_user)
    elif current_page == "admin":
        await admin_user_page(controller, access_token_user)
    elif current_page == "shop":
        from page.admin_shop import admin_shop_page
        await admin_shop_page(controller, access_token_user)
    elif current_page == "admin_order":
        from page.order_admin import order_admin_page
        await order_admin_page(controller, access_token_user)
    elif current_page == "phone":
        from page.phone_admin import admin_phone_page
        await admin_phone_page(controller, access_token_user)
    else:
        st.error("404 - Page not found")
        
if __name__ == "__main__":
    asyncio.run(main())