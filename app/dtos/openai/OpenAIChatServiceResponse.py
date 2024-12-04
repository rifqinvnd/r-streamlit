from openai.types.chat.chat_completion import Choice, ChatCompletion
from pydantic import BaseModel
from typing import Any, Dict, Optional, Union


class ChatResponse(BaseModel):
    completion: Choice | ChatCompletion | Any
    cost: float = None

class OpenAIChatServiceResponse(BaseModel):
    error: bool
    data: Optional[
        Union[
            ChatResponse,
            Dict[str, Any],
        ]
    ]
    message: str
