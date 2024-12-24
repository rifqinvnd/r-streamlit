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
        if st.session_state.page_name != page_name:
            st.session_state.messages = []
            st.session_state.conversation_title = ""
            st.session_state.conversation_id = ""
        
        st.session_state.page_name = page_name
        
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
                        st.session_state.user_id = user_id
                        
                        self.database_service.log_login_activity(user_id)

                        st.success("Logged in successfully!")
                        time.sleep(1)
                        st.rerun()
                    
                    st.error("Outsiders not allowed!")
                    
                st.error("Fill your username and password correctly!")
    
    def chat_page(self):
        st.title("💬 Ripki AI")
        st.write(
            "Salutations, esteemed user! "
            "My name is Ripki AI. I'm your daily dose of companion for all things experimental and geeky. "
            "Ready to dive into a world of intriguing questions and answers? "
        )
        
        if st.session_state.conversation_title:
            st.subheader(st.session_state.conversation_title, divider=True)
            
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if st.session_state.messages or st.session_state.page_name == "Ripki AI":
            if new_message := st.chat_input("How can I assist your little curiousity today?"):
                st.session_state.messages.append({"role": "user", "content": new_message})
                
                with st.chat_message("user"):
                    st.markdown(new_message)
                
                user_data = self.database_service.get_user_data(st.session_state.username)
                
                if not st.session_state.conversation_id:
                    conversation_title = self.ai_service.define_conversation_title(new_message)
                    st.session_state.conversation_title = conversation_title
                    
                    conversation_data = self.database_service.insert_conversation_title(conversation_title, user_data.get("id"))
                    st.session_state.conversation_id = conversation_data["id"]
                
                user_profile = {
                    "profile": user_data.get("profile", ""),
                    "likes": user_data.get("likes", ""),
                    "dislikes": user_data.get("dislikes", "",),
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
                        conversation_id=st.session_state.conversation_id,
                    )
                )
                
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    def new_chat_page(self):
        self.chat_page()
    
    def chat_history_page(self):
        chat_history = self.database_service.get_chat_history(st.session_state.username)
        chat_history = [chat for chat in chat_history if chat["conversation_id"]]
        conversation_ids = set([chat["conversation_id"] for chat in chat_history if chat["conversation_id"]])
        
        conversations = self.database_service.get_conversation_titles(list(conversation_ids))
        conversation_titles = [conversation["title"] for conversation in conversations]
            
        selected_history = st.selectbox(label="Select chat history", options=conversation_titles)
        
        if st.button('Get chat history', key='chat_history'):
            st.session_state.conversation_id = [
                conversation["id"] 
                for conversation in conversations
                if conversation["title"] == selected_history
            ][0]
            
            if (
                selected_history != st.session_state.conversation_title
                or not st.session_state.conversation_title
            ):
                st.session_state.messages = self.process_chat_history(chat_history)
            
            st.session_state.conversation_title = selected_history
            
        self.chat_page()
        
    def process_chat_history(self, chat_history: list[dict]):
        chat_history = [
            chat for chat in chat_history
            if chat["conversation_id"] == st.session_state.conversation_id
        ]
        
        messages = []
        
        for history in chat_history:
            messages.append({"role": "user", "content": history["message"]})
            messages.append({"role": "assistant", "content": history["response"]})

        return messages
