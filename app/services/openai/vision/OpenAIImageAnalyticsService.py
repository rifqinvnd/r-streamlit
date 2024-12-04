import json
from typing import List, Union

from app.common.decorator import func_logger
from app.common.error import BadRequest
from app.common.log import logger
from app.dtos.openai import OpenAICreateChatVisionDto
from app.dtos.openai.vision import OpenAIInstagramStoryInsightDto

from ..OpenAIChatVisionService import OpenAIChatVisionService


class OpenAIImageAnalyticsService(OpenAIChatVisionService):
    @func_logger
    def detect_instagram_story_insights(
        self, image_paths: Union[List[str], str] = None, image_urls: Union[List[str], str] = None,
    ) -> dict:
        logger.info("Detecting Instagram Story Insight data...")
           
        prompts = [
            "You are an expert in reading insights data of an image and write it down according to the given response format.",
            "You will be given by Instagram story image with its insights.",
            "You have to write down every single aspect possible that you found on the image into the given response format.",
            "Fill any missing data by null value.",
        ]
        
        messages = [
            self.create_message_with_images(
                content=prompts,
                image_paths=image_paths,
                image_urls=image_urls,
            )
        ]
        
        response = self.create_chat_vision(
            OpenAICreateChatVisionDto(
                messages=messages,
                model="gpt-4o-2024-08-06",
                response_format=OpenAIInstagramStoryInsightDto,
                max_tokens=16000,
            )
        )
        
        if response.error:
            raise BadRequest(response.message)
        
        result = OpenAIInstagramStoryInsightDto.model_validate(
            json.loads(response.data.completion.message.content)
        ).model_dump()
        
        logger.info("Success detecting image analytics data!")
        logger.custom_info(result)
        
        return result
        