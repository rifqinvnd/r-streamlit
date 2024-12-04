from pydantic import BaseModel


class AIChatUserDto(BaseModel):
    name: str
    id: str
    language: str = "en"

class AIChatDto(BaseModel):
    user: AIChatUserDto = None
    message: str
    stream: bool = False
