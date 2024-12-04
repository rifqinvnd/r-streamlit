import streamlit as st
import uuid
from supabase import create_client, Client

from app.common.error import BadRequest
from app.common.log import logger


class DatabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            supabase_url=st.secrets["SUPABASE_URL"],
            supabase_key=st.secrets["SUPABASE_KEY"]
        )
    
    def get_user_data(self, username: str):
        try:
            response = self.supabase.table("users").select("*").eq("username", username).execute()

            if response.data:
                return response.data[0]
            
            return {}
        except Exception as e:
            st.error(f"[Database] Error fetching user data: {e}")
            return {}
        
    def save_chat(self, message: str, response: str):
        data = {
            "user_id": str(uuid.uuid4()),
            "message": message,
            "response": response,
        }
        
        try:
            self.supabase.table("chat_history").insert(data).execute()
            
            logger.info("[Database] Chat saved successfully!")
        except Exception as e:
            logger.error(f"[Database] Error saving chat: {e}")
            raise BadRequest(f"[Database] Error saving chat: {e}")

    def get_chat_history(self, username: str):
        user_id = self.get_user_id(username)
        
        if not user_id:
            st.error("No user found with that username.")
            return []
        
        try:
            response = self.supabase.table("chat_history").select("*").eq("user_id", user_id).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"[Database] Error fetching chat history: {e}")
            return []
