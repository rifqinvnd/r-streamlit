import base64
import openai
import os
import requests
import tempfile
from openai.types.chat import ChatCompletionUserMessageParam
from typing import Dict, List, Union

from app.common.decorator import func_logger
from app.common.error import BadRequest
from app.common.log import logger
from app.dtos.openai import (
    OpenAICreateChatVisionDto,
    OpenAIChatServiceResponse,
    ChatResponse,
)

from .OpenAIService import OpenAIService


class OpenAIChatVisionService(OpenAIService):
    @func_logger
    def create_chat_vision(self, args: OpenAICreateChatVisionDto) -> OpenAIChatServiceResponse:
        try:
            logger.info(f"[OPENAI] chat vision {args.model}")
            
            args = args.model_dump(exclude_none=True)

            completion = openai.beta.chat.completions.parse(
                **args,
                timeout=300,
            )
            
            response_format = args.get("response_format")
            
            if response_format:
                response_format = response_format.model_json_schema() if not isinstance(response_format, dict) else response_format
            
            for message in args["messages"]:
                if not isinstance(message["content"], dict | str):
                    message["content"] = {key: value for key, value in message["content"]}
                        
            logger.info("[OPENAI] [LOG] chat vision completion response")
            logger.custom_info(
                {
                    "id": completion.id,
                    "parameters": {
                        "prompt": args["messages"], 
                        "model": args["model"], 
                        "response_format": response_format,
                    },
                    "completion": completion.model_dump(),
                }
            )

            return OpenAIChatServiceResponse(
                error=False,
                data=ChatResponse(completion=completion.choices[0]),
                message="Success!",
            )
        except Exception as e:
            return self.handle_openai_exception(e)

    def create_message_with_images(
        self, 
        content: Union[List[str], str], 
        image_paths: Union[List[str], str] = None, 
        image_urls: Union[List[str], str] = None,
    ) -> ChatCompletionUserMessageParam:
        """
        Creates a message dictionary containing images encoded in base64.

        Args:
            content (list of str or str): List of str content or str content of the prompt.
            image_paths (list of str or str): List of image file paths or file path.
            image_urls (list of str or str): List of image url or image url.

        Returns:
            dict: Message dictionary ready to be used with the OpenAI API.
        """
                
        content = [
            {
                "type": "text",
                "text": "\n".join(content) if isinstance(content, list) else content,
            }
        ]
        
        if image_paths:
            if isinstance(image_paths, str):
                image_paths = [image_paths]
                
            for path in image_paths:
                content.append(self.__format_image(path, is_path=True))
                
        if image_urls:
            if isinstance(image_urls, str):
                image_urls = [image_urls]
                
            for url in image_urls:
                content.append(self.__format_image(url))

        return ChatCompletionUserMessageParam(
            content=content,
            role="user",
        )
    
    def __encode_image_to_base64(self, file_path: str) -> str:
        """
        Encodes a given image file to base64.

        Args:
            file_path (str): Path to the image file.

        Returns:
            str: Base64 encoded string of the image.
        """
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    @func_logger
    def __format_image(self, image: str, is_path: bool = False) -> Dict:
        if not is_path:
            response = requests.get(image)
            
            if response.status_code != 200:
                raise BadRequest(f"OpenAIChatVision Error: Failed to download image from URL: {image}")
                
            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Encode the image to base64
            image = self.__encode_image_to_base64(temp_file_path)
            
            # Clean up the temporary file
            os.remove(temp_file_path)
        else:
            image = self.__encode_image_to_base64(image)

        image = f"data:image/png;base64,{image}"

        return {
            "type": "image_url",
            "image_url": {
                "url": image
            }
        }
