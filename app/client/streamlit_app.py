import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logging
import asyncio
from page.login import login_page
from page.register import register_page
from page.home import home_page
from api_call import refresh_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS 
from streamlit_cookies_controller import CookieController

APP_TITLE = "Hieu's AI Assistant"
APP_ICON = "🤖"


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
        content: "🚀 Hieu's AI Dashboard";
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
    
    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        await asyncio.sleep(0.1)
        st.rerun()
    controller = CookieController()
    access_token_user = controller.get('access_token_user')
    refresh_access_user = controller.get('refresh_token_user')
    # print("Access token from cookie:", access_token_user)
    # print("Refresh token from cookie:", refresh_access_user)
    if access_token_user is None and refresh_access_user is None or refresh_access_user is None:
        #login_page(controller)
        home_page(controller, None)
        return
    elif access_token_user is None and refresh_access_user is not None:
        #print("No access token, but refresh token found. Attempting to refresh...")
        if not refresh_access_token(refresh_access_user.get('refresh_token'), controller):
            st.info("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.")
        #print("Cookie found:", usernameCookie)
            return
        else:
            controller.set('access_token_user', access_token_user, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, path='/')
    else:
        controller.set('access_token_user', access_token_user, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, path='/')
        controller.set('refresh_token_user', refresh_access_user, max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, path='/')
    params = st.query_params
    current_page = params.get("page", "login")
    
    if current_page == "login":
        login_page(controller)
    elif current_page == "register":
        register_page()
    elif current_page == "home":
        home_page(controller, access_token_user.get('access_token'))
    else:
        st.error("404 - Page not found")
        
if __name__ == "__main__":
    asyncio.run(main())