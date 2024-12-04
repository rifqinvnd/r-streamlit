import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import streamlit_option_menu

from app.common.enums import SidebarEnum
from app.services import PageService


page_service = PageService()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

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
        st.session_state.user_email = None
        st.rerun()
