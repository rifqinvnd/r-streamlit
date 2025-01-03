from pydantic import BaseModel


class UpdateUserDataDto(BaseModel):
    id: int
    likes: str = None
    dislikes: str = None
    language: str = None
