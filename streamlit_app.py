import rollbar
import streamlit as st
import streamlit_option_menu

from app.common.enums import SidebarEnum
from app.common.log import logger
from app.services import PageService, RollbarService


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

logger.info("[Streamlit] Starting app...")
RollbarService.initialize()
page_service = PageService()
logger.info("[Streamlit] App initialized!")

try:
    
    if not st.session_state.logged_in:
        page_service.login_page()
    else:
        with st.sidebar.expander("Page Selection", expanded=True):
            selected_page = streamlit_option_menu.option_menu(
                menu_title='R Project',
                options=list(SidebarEnum.keys()),
                icons=[logo["logo"] for logo in SidebarEnum.values()],
                menu_icon=':dash:',
            )
        
        page_service.map_pages(page_name=selected_page)

        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()
            
except Exception as e:
    st.error(str(e))
    logger.error(str(e))
    rollbar.report_exc_info()
