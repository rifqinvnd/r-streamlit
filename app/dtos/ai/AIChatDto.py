from pydantic import BaseModel


class AIChatUserDto(BaseModel):
    name: str
    id: int
    language: str = "en"
    data: dict = {}

class AIChatAgentDto(BaseModel):
    id: int
    name: str
    model: str

class AIChatDto(BaseModel):
    message: str
    user: AIChatUserDto = None
    agent: AIChatAgentDto = None
    model: str = "gpt-4o-mini"
    stream: bool = False
