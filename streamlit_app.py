import extra_streamlit_components as stx
import rollbar
import streamlit as st
import streamlit_option_menu
import time

from app.common.enums import SidebarEnum
from app.common.log import logger
from app.services import (
    AuthenticationService,
    DatabaseService,
    PageService, 
    RollbarService,
)


# Instantiate session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = ""

if 'conversation_title' not in st.session_state:
    st.session_state.conversation_title = ""
    
if 'page_name' not in st.session_state:
    st.session_state.page_name = ""

if 'agent' not in st.session_state:
    st.session_state.agent = {}

logger.info("[Streamlit] Starting app...")

with st.empty():
    @st.cache_resource
    def get_manager():
        return stx.CookieManager()

    cookie_manager = get_manager()

def get_cookie(cookie: str) -> str | None:
    try:
        return cookie_manager.get(cookie)
    except:
        logger.warning(f"[Authentication] Cookie '{cookie}' doesn't exist!")
        return None

def set_cookie(cookie: str, value: str) -> None:
    try:
        cookie_manager.set(cookie, value, key=cookie)
    except:
        logger.warning(f"[Authentication] Failed to set Cookie '{cookie}' with value '{value}'!")

def delete_cookie(cookie: str) -> None:
    try:
        cookie_manager.delete(cookie, key=f"delete_{cookie}")
    except:
        logger.warning(f"[Authentication] Failed to delete Cookie '{cookie}'!")

def delete_login_cookies() -> None:
    delete_cookie("logged_in")
    delete_cookie("username")
    delete_cookie("user_id")

authentication_service = AuthenticationService()
database_service = DatabaseService()
page_service = PageService()
RollbarService.initialize()

logger.info("[Streamlit] App initialized!")

try:
    def login_page():
        st.title('Welcome to R Project!')
        # st.logo("ALVA_White.png")

        # Set login form
        with st.form("login"):
            username = st.text_input("Input your username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
        
            if login_button:
                if username and password:
                    # Authenticate username and password
                    if authentication_service.authenticate(username, password):
                        # Set session state logged in
                        st.session_state.logged_in = True
                        st.session_state.username = username

                        # Set session user id
                        user_id = database_service.get_user_data(username)["id"]
                        st.session_state.user_id = user_id
                                                
                        # Log login activity
                        database_service.log_login_activity(user_id)

                        # Add description and rerun streamlit
                        st.success("Logged in successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    
                    st.error("Outsiders not allowed!")
                    
                st.error("Fill your username and password correctly!")

    # Check if cookie login available
    if get_cookie("logged_in"):
        st.session_state.logged_in = True
        st.session_state.username = get_cookie("username")
        st.session_state.user_id = get_cookie("user_id")
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        if not get_cookie("logged_in"):
            set_cookie("logged_in", True)
        
        if not get_cookie("username"):
            set_cookie("username", st.session_state.username)
        
        if not get_cookie("user_id"):
            set_cookie("user_id", st.session_state.user_id)
        
        with st.sidebar.expander("Page Selection", expanded=True):
            selected_page = streamlit_option_menu.option_menu(
                menu_title='R Project',
                options=list(SidebarEnum.keys()),
                icons=[logo["logo"] for logo in SidebarEnum.values()],
                menu_icon=':dash:',
            )
        
        page_service.map_pages(page_name=selected_page)

        if st.sidebar.button("Logout", on_click=delete_login_cookies):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = ""
            st.session_state.messages = []
            st.session_state.conversation_id = ""
            st.session_state.conversation_title = ""
            st.session_state.page_name = ""
            st.session_state.agent = {}
            
            st.rerun()
            
except Exception as e:
    st.error(str(e))
    logger.error(str(e))
    rollbar.report_exc_info()
