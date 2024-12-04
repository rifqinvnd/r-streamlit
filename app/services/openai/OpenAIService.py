import openai
import streamlit as st

from app.common.log import logger
from app.dtos.openai import OpenAIChatServiceResponse
from app.common.enums.openai import OPENAI_ERROR_MESSAGE_ENUM


class OpenAIService:
    def __init__(self):
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        
    def handle_openai_exception(self, exception: Exception) -> OpenAIChatServiceResponse:
        message = OPENAI_ERROR_MESSAGE_ENUM.get(
            type(exception).__name__, 
            f"[OPENAI] service error: {exception}",
        )

        logger.error(message)
        return OpenAIChatServiceResponse(error=True, data={}, message=message)
