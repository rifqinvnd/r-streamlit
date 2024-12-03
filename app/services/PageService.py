import streamlit as st
import time
from openai import OpenAI

from .AuthenticationService import AuthenticationService


class PageService:
    def __init__(self):
        self.authentication_service = AuthenticationService()
        self.database_service = ""

    def login_page(self):
        st.title('Welcome to R Project!')
        # st.logo("ALVA_White.png")

        with st.form("Login"):
            username = st.text_input("Input your username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if self.authentication_service.authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username

                    # log_login_activity(username)

                    st.success("Logged in successfully!")
                    time.sleep(1)
                    st.rerun()
                
                st.error("Password is incorrect. You can retry or ask the data team for the correct password.")
    
    def chatbot_page(self):
        st.title("💬 Chatbot")
        st.write(
            "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
            "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
            "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
        )
        
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Hello, I'm Ripki AI. How can I help you today?"):

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                stream=True,
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
