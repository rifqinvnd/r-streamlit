from pydantic import BaseModel


class InsertUserChatHistoryDto(BaseModel):
    user_id: int
    message: str
    response: str
