from pydantic import BaseModel


class AIChatUserDto(BaseModel):
    name: str
    id: str
    language: str = "en"
    data: dict = {}

class AIChatDto(BaseModel):
    user: AIChatUserDto = None
    message: str
    stream: bool = False
