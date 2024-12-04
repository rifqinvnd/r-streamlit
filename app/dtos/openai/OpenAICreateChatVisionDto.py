from app.common.enums.openai import OpenAIVisionModelEnum

from .OpenAICreateChatDto import OpenAICreateChatDto


class OpenAICreateChatVisionDto(OpenAICreateChatDto):
    model: OpenAIVisionModelEnum
    max_tokens: int = 1000
