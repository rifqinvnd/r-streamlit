from openai.types.chat import ChatCompletionMessageParam
from typing import List

from .AIChatDto import AIChatDto


class AIPromptDto(AIChatDto):
    category: str = None
    prompts: List[ChatCompletionMessageParam] = None
