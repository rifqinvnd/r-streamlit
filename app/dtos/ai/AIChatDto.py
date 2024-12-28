from pydantic import BaseModel


class AIChatUserDto(BaseModel):
    name: str
    id: int
    language: str = "en"
    data: dict = {}

class AIChatDto(BaseModel):
    user: AIChatUserDto = None
    message: str
    model: str = "gpt-4o-mini"
    stream: bool = False
