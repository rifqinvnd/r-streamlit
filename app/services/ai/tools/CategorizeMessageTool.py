from pydantic import BaseModel, Field
from enum import Enum


class CategorizeMessageTool(BaseModel):
    """Tool to categorize message."""
    category: str = Field(
        ...,
        description="The category of the message according to the listed category"
    )

class CategoryEnum(Enum):
    greetings = "For greeting messages like 'Hello', 'Hi', etc."
    simple_conversation = "For messages that are easy to understand and casual."
    deep_conversation = "For messages that are asking about deep topics in any field or asking for opinion."
    
    @classmethod
    def to_dict(cls):
        return {member.name: member.value for member in cls}
    
    @classmethod
    def to_list(cls):
        return [member.name for member in cls]

class CategoryModelEnum(Enum):
    greetings = "gpt-4o-mini"
    simple_conversation = "gpt-4o-mini"
    deep_conversation = "o1-preview"
    
    @classmethod
    def to_dict(cls):
        return {member.name: member.value for member in cls}
