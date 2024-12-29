import json
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionNamedToolChoiceParam,
    ChatCompletionToolParam,
)
from typing import List

from app.common.decorator import func_logger
from app.common.error import BadRequest
from app.common.log import logger
from app.dtos.ai import AIChatDto
from app.dtos.openai import OpenAICreateChatDto
from app.services import DatabaseService
from app.services.openai import OpenAIChatService
from .tools import (
    CategorizeMessageTool,
    CategoryEnum,
)


class AIService:
    def __init__(self) -> None:
        self.database_service = DatabaseService()
        self.openai_chat_service = OpenAIChatService()
    
    @func_logger
    def chat(self, args: AIChatDto) -> str:
        response = self.openai_chat_service.create_chat(
            OpenAICreateChatDto(
                messages=self.get_ai_prompt(args),
                model=args.model,
                user=str(args.user.id),
                stream=args.stream,
            )
        )
        
        if response.error:
            raise BadRequest(f"Failed to get response from OpenAI: {response.message}!")
        
        return response.data.completion
    
    @func_logger
    def categorize_message(self, args: AIChatDto) -> str:
        response = self.openai_chat_service.create_chat(
            OpenAICreateChatDto(
                messages=self.get_categorize_message_prompt(args.message),
                model="gpt-4o-mini",
                user=args.user.id,
                tools=[self.get_categorize_message_tool()],
                tool_choice=ChatCompletionNamedToolChoiceParam(
                    type="function",
                    function={"name": "categorize_message"}
                )
            )
        )
        
        if response.error:
            raise BadRequest(f"Failed to get response from OpenAI: {response.message}!")
        
        response = CategorizeMessageTool.model_validate(
            json.loads(response.data.completion.message.tool_calls[0].function.arguments)
        ).model_dump()
        
        return response["category"]

    @func_logger
    def define_conversation_title(self, message: str) -> str:
        response = self.openai_chat_service.create_chat(
            OpenAICreateChatDto(
                messages=self.get_define_conversation_title_prompt(message),
                model="gpt-4o-mini",
            )
        )
        
        if response.error:
            raise BadRequest(f"Failed to get response from OpenAI: {response.message}!")
        
        return response.data.completion.message.content.replace('"', "")

    @func_logger
    def get_ai_prompt(self, args: AIChatDto) -> List[ChatCompletionMessageParam]:
        prompts = []
        
        if args.agent:
            ai_agent_prompts = self.database_service.get_ai_agent_prompts(args.agent.id)
        
            for prompt in ai_agent_prompts:
                prompts.append(
                    {
                        "name": prompt["prompt_name"], 
                        "content": prompt["content"], 
                        "role": prompt["role"]
                    }
                )
            
        if args.user:
            user_prompt = [
                "You have received a new message from user:",
                f"Name: {args.user.name}",
                f"Language: {args.user.language}",
            ]
            
            if args.user.data:
                user_prompt.extend(
                    [f"{key.capitalize()}: {value}" for key, value in args.user.data.items()]
                )
            
            prompts.append(
                {
                    "content": "\n".join(user_prompt),
                    "role": "user",
                    "name": "user-profile",
                }
            )
        
        prompts.append(
            {
                "content": f"New Message: {args.message}",
                "role": "user",
                "name": "new-message",
            }
        )
        
        prompts = [
            ChatCompletionUserMessageParam(**prompt) 
            if prompt["role"] == "user" 
            else ChatCompletionSystemMessageParam(**prompt)
            for prompt in prompts 
        ]
        
        return prompts
    
    def get_categorize_message_prompt(self, message: str) -> List[ChatCompletionMessageParam]:
        categories = [f"- {key}: {value}" for key, value in CategoryEnum.to_dict().items()]
        profile = [
            "You are an expert in categorizing message.",
            "You have to determine whether the message best fits into one of the category available.",
            "The available categories are:",
            "\n".join(categories),
            
            "\nGive only one category for the message."
        ]
        
        return [
            ChatCompletionSystemMessageParam(
                role="system",
                content="\n".join(profile),
                name="profile",
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=f"Categorize this message: {message}",
                name="new-message",
            )
        ]
    
    def get_categorize_message_tool(self) -> ChatCompletionToolParam:
        schema = CategorizeMessageTool.model_json_schema()
        
        schema["name"] = "categorize_message"
        schema["properties"]["category"]["enum"] = CategoryEnum.to_list()
        
        return ChatCompletionToolParam(
            type="function",
            function={
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema,
            }
        )
    
    def get_define_conversation_title_prompt(self, message: str) -> List[ChatCompletionMessageParam]:
        profile = [
            "You are an expert in determining a conversation title.",
            "You have to determine which title best summarizing the core of the conversation.",
            "Ensure the title is concise and descriptive with no more than 6-8 words.",
        ]
        
        return [
            ChatCompletionSystemMessageParam(
                role="system",
                content="\n".join(profile),
                name="profile",
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=f"Determine the title of this message: {message}",
                name="new-message",
            )
        ]
