import openai

from app.common.log import logger
from app.dtos.openai import (
    OpenAICreateChatDto,
    OpenAIChatServiceResponse,
    ChatResponse,
)
from app.common.enums.openai import OPENAI_MODEL_COST_ENUM

from .OpenAIService import OpenAIService


class OpenAIChatService(OpenAIService):
    def create_chat(self, args: OpenAICreateChatDto) -> OpenAIChatServiceResponse:
        try:
            logger.info(f"[OPENAI] chat {args.model}")
            
            args = args.model_dump(exclude_none=True)

            completion = openai.chat.completions.create(
                **args,
                timeout=300,
            )
            
            if args.get("stream", False):
                logger.info("[OPENAI] [LOG] chat completion streaming response...")
                return OpenAIChatServiceResponse(
                    error=False,
                    data=ChatResponse(completion=completion),
                    message="Success!",
                )

            cost = {
                "prompt": OPENAI_MODEL_COST_ENUM[args["model"]]["prompt"],
                "completion": OPENAI_MODEL_COST_ENUM[args["model"]]["completion"],
            }

            prompt_token = completion.usage.prompt_tokens
            prompt_usage = prompt_token / 1000 * cost["prompt"]
            
            logger.info(
                f"[OPENAI] chat prompt token: {prompt_token} ($ {prompt_usage} => Rp {prompt_usage * 15000})"
            )

            completion_token = completion.usage.completion_tokens
            completion_usage = completion_token / 1000 * cost["completion"]
            
            logger.info(
                f"[OPENAI] chat completion token: {completion_token} ($ {completion_usage} => Rp {completion_usage * 15000})"
            )

            total_tokens = completion.usage.total_tokens
            total_usage = prompt_usage + completion_usage
            
            logger.info(
                f"[OPENAI] chat total tokens: {total_tokens} ($ {total_usage} => Rp {total_usage * 15000})"
            )

            cost = total_usage * 15000

            logger.info("[OPENAI] [LOG] chat completion response")
            logger.custom_info(
                {
                    "id": completion.id,
                    "parameters": {"prompt": args["messages"], "model": args["model"], "tools": args.get("tools")},
                    "completion": completion.model_dump(),
                    "cost": cost,
                }
            )

            return OpenAIChatServiceResponse(
                error=False,
                data=ChatResponse(completion=completion.choices[0], cost=cost),
                message="Success!",
            )
        except Exception as e:
            return self.handle_openai_exception(e)
