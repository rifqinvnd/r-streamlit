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

def initialize_app():
    RollbarService.initialize()
    page_service = PageService()

    try:
        logger.info("[Streamlit] Starting app...")
        if not st.session_state.logged_in:
            page_service.login_page()
        else:
            with st.sidebar.expander("Page Selection", expanded=True):
                selected_page = streamlit_option_menu.option_menu(
                    menu_title='R Project',
                    options=list(SidebarEnum.keys()),
                    icons=[logo["logo"] for logo in SidebarEnum.values()],
                    menu_icon='robot',
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

# Initialize Streamlit app
initialize_app()
