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
from app.dtos.ai import AIChatDto, AIPromptDto
from app.dtos.openai import OpenAICreateChatDto
from app.services.openai import OpenAIChatService
from .tools import (
    CategorizeMessageTool,
    CategoryEnum,
    CategoryModelEnum,
)


class AIService:
    def __init__(self) -> None:
        self.openai_chat_service = OpenAIChatService()
    
    @func_logger
    def chat(self, args: AIChatDto) -> str:
        category = self.categorize_message(args)
                
        response = self.talk(
            AIPromptDto(
                **args.model_dump(),
                category=category,
                prompts=self.get_ai_prompt(args, category)
            )
        )

        return response
    
    @func_logger
    def talk(self, args: AIPromptDto) -> str:
        model = CategoryModelEnum.to_dict().get(args.category)
        
        logger.info(CategoryModelEnum.to_dict())
        
        if not model:
            logger.warn(f"Category '{args.category}' is not a valid category!")
            model = "gpt-4o-mini"
        
        response = self.openai_chat_service.create_chat(
            OpenAICreateChatDto(
                messages=args.prompts,
                model=model,
                user=args.user.id,
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
    def get_ai_prompt(self, args: AIChatDto, category: str) -> List[ChatCompletionMessageParam]:
        prompts = []
        
        profile = [
            "Your name is Ripki AI",
            "You are created by Rifqi, an AI Engineer specialist.", 
            "Rifqi is an AI Engineer, working at a Marketing Agency company called \"Olrange\".", 
            "Rifqi has a girlfriend named Nasya.",
            
            "You are a nerd that experts in any fields of works.",
            "You have to be detailed on giving even unnecessary things like a nerd",
            "You have mastered any study, work, or even hobby related activity.",
             
            "In giving your response, you always have a deep thought to give the most geeky answer.",
        ]
        
        # TODO: MAPPING, MOVE TO EITHER ENUMS OR DB
        role = "user" if category == "deep_conversation" else "system"
        
        prompts.append(
            {
                "content": "\n".join(profile),
                "role": role,
                "name": "profile",
            }
        )
        
        response_format = [
            "You will give your response in a nerdy, geek, and professorized character.",
            "Give your response in plain text without markdown formatting!",
        ]
        
        prompts.append(
            {
                "content": "\n".join(response_format),
                "role": role,
                "name": "response-format",
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
                    "role": role,
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
            if prompt.get("role") == "user" 
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
