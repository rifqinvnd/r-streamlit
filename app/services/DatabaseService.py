import json
import streamlit as st
from supabase import create_client, Client

from app.common.error import BadRequest
from app.common.decorator import func_logger
from app.common.log import logger
from app.dtos.database import InsertUserChatHistoryDto


class DatabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            supabase_url=st.secrets["SUPABASE_URL"],
            supabase_key=st.secrets["SUPABASE_KEY"]
        )
    
    @func_logger
    def get_ai_agents(self, user_id: int) -> dict:
        try:
            response = self.supabase.rpc("get_ai_agents", params={"user_id": user_id}).execute()

            return response.data
        except Exception as e:
            logger.error(f"[Database] Error getting AI agent: {e}")
            return {}
    
    @func_logger
    def get_ai_agent_prompts(self, user_id: int) -> list[dict]:
        try:
            response = self.supabase.rpc("get_ai_agent_prompts", params={"user_id": user_id}).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"[Database] Error getting AI agent prompts for user id {user_id}: {e}")
            return []
    
    def get_user_data(self, username: str) -> dict:
        try:
            response = self.supabase.table("users").select("*").eq("username", username).execute()

            if response.data:
                return response.data[0]
            
            return {}
        except Exception as e:
            st.error(f"[Database] Error fetching user data: {e}")
            return {}

    def get_chat_history(self, username: str) -> list[dict]:
        user_id = self.get_user_data(username)["id"]
        
        if not user_id:
            st.error("No user found with that username.")
            return []
        
        try:
            response = (
                self.supabase
                .table("user_chat_history")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            return response.data
        except Exception as e:
            logger.error(f"[Database] Error fetching chat history: {e}")
            return []

    def insert_chat_history(self, data: InsertUserChatHistoryDto) -> None:
        try:
            self.supabase.table("user_chat_history").insert(data.model_dump()).execute()
            
            logger.info("[Database] Chat saved successfully!")
        except Exception as e:
            logger.error(f"[Database] Error saving chat: {e}")
            raise BadRequest(f"[Database] Error saving chat: {e}")
    
    def log_login_activity(self, user_id: int) -> None:
        try:
            self.supabase.table("user_activity_logs").insert({"user_id": user_id}).execute()
            
            logger.info("[Database] User login activity logged successfully!")
        except Exception as e:
            logger.error(f"[Database] Error logging user login activity: {e}")
            raise BadRequest(f"[Database] Error logging user login activity: {e}")
    
    def insert_conversation_title(self, conversation_title: str, user_id: int) -> dict:
        try:
            response = self.supabase.table("user_chat_titles").insert({"title": conversation_title, "user_id": user_id}).execute()
            
            logger.info("[Database] User chat title inserted successfully!")

            return response.data[0]
        except Exception as e:
            logger.error(f"[Database] Error inserting user chat title: {e}")
            raise BadRequest(f"[Database] Error inserting user chat title: {e}")
    
    def get_conversation_titles(self, conversation_ids: int | list[int]) -> list[dict]:
        if isinstance(conversation_ids, int):
            conversation_ids = [conversation_ids]
        
        try:
            response = self.supabase.table("user_chat_titles").select("*").in_("id", conversation_ids).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"[Database] Error fetching conversations: {e}")
            return []
        