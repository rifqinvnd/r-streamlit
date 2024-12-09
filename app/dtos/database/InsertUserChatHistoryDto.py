from pydantic import BaseModel


class InsertUserChatHistoryDto(BaseModel):
    user_id: int
    username: str
    message: str
    response: str
    category: str = None
