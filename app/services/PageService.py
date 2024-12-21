import streamlit as st
import time

from app.common.enums import SidebarEnum
from app.dtos.database import InsertUserChatHistoryDto
from app.dtos.ai import AIChatDto, AIChatUserDto
from app.services import DatabaseService
from app.services.ai import AIService

from .AuthenticationService import AuthenticationService


class PageService:
    def __init__(self):
        self.authentication_service = AuthenticationService()
        self.database_service = DatabaseService()
        self.ai_service = AIService()
    
    def map_pages(self, page_name: str):
        function_map = {name: getattr(self, config["func"]) for name, config in SidebarEnum.items()}
        
        function_map[page_name]()

    def login_page(self):
        st.title('Welcome to R Project!')
        # st.logo("ALVA_White.png")

        with st.form("login"):
            username = st.text_input("Input your username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if username and password:
                    if self.authentication_service.authenticate(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username

                        user_id = self.database_service.get_user_data(username)["id"]
                        self.database_service.log_login_activity(user_id)

                        st.success("Logged in successfully!")
                        time.sleep(1)
                        st.rerun()
                    
                    st.error("Outsiders not allowed!")
                    
                st.error("Fill your username and password correctly!")
    
    def chatbot_page(self):
        st.title("💬 Ripki AI")
        st.write(
            "Salutations, esteemed user! "
            "My name is Ripki AI. I'm your daily dose of companion for all things experimental and geeky. "
            "Ready to dive into a world of intriguing questions and answers? "
        )
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if new_message := st.chat_input("How can I assist your little curiousity today?"):
            st.session_state.messages.append({"role": "user", "content": new_message})
            
            with st.chat_message("user"):
                st.markdown(new_message)
            
            user_data = self.database_service.get_user_data(st.session_state.username)
            user_profile = {
                "profile": user_data.get("profile", ""),
                "likes": user_data.get("likes", ""),
                "dislikes": user_data.get("dislikes", "",)
            }

            stream = self.ai_service.chat(
                AIChatDto(
                    user=AIChatUserDto(
                        name=user_data.get("name", st.session_state.username),
                        id=str(user_data.get("id", "99999")),
                        language=user_data.get("language", "en"),
                        data=user_profile,
                    ),
                    message=new_message,
                    stream=True,
                )
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            
            self.database_service.insert_chat_history(
                InsertUserChatHistoryDto(
                    user_id=user_data["id"],
                    message=new_message,
                    response=response,
                )
            )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
