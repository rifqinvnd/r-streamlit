from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionToolChoiceOptionParam,
)

from app.common.enums.openai import OpenAIModelEnum


class OpenAICreateChatDto(BaseModel):
    messages: List[ChatCompletionMessageParam]
    model: OpenAIModelEnum
    response_format: Optional[Union[Dict, BaseModel, Any]] = {"type": "text"}
    stream: bool = False
    tools: Optional[List[ChatCompletionToolParam]] = None
    tool_choice: Optional[ChatCompletionToolChoiceOptionParam] = None
    user: Optional[str] = None
    extra_body: Optional[dict] = {}
