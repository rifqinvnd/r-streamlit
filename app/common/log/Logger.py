import colorlog
import os
import json
import logging

from uuid import uuid4


class Logger(logging.Logger):
    """Custom logger class"""

    dir = "logs"
    info_file = "logs/info.log"
    error_file = "logs/error.log"
    name = "app"
    logger = None

    def __init__(self, level=logging.INFO):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level)
        formatter = colorlog.ColoredFormatter(
            fmt="[%(log_color)s%(asctime)s%(reset)s] [%(log_color)s%(levelname)s%(reset)s]: %(message)s",
            log_colors={
                "DEBUG": "CYAN",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.__setup_handlers(level, formatter)

    def debug(self, msg: object, *args: object):
        """Debug log"""
        self.logger.debug(msg, *args)

    def info(self, msg: object, *args: object):
        """Info log"""
        self.logger.info(msg, *args)

    def error(self, msg: object, *args: object):
        """Error log"""
        self.logger.error(msg, *args)

    def warning(self, msg: object, *args: object):
        """Warning log"""
        self.logger.warning(msg, *args)

    def critical(self, msg: object, *args: object):
        """Critical log"""
        self.logger.critical(msg, *args)

    def custom_info(self, data: dict | list | str):
        """Custom info log"""
        if isinstance(data, dict) or isinstance(data, list):
            self.info(f"\n{json.dumps(data, indent=4)}")
        elif isinstance(data, str):
            self.info(data)

    def custom_received_message(self, request):
        """Custom received message log"""
        self.get_request_id(request)

        self.info(
            f"{request.remote_addr} - - '{request.method} {request.path}' | Request Received"
        )
        self.custom_info(
            {
                "request_id": request.id,
                "headers": dict(request.headers),
                "body": self.get_request_body(request),
                "params": request.args,
            }
        )

    def custom_response_message(self, request, response):
        """Custom response message log"""
        self.get_request_id(request)
        
        if response.status_code == 404:
            self.logger.warning(
                f"{request.remote_addr} - - '{request.method} {request.path}' {response.status_code} | Resource Not Found"
            )

        elif response.status_code >= 400:
            self.logger.error(
                f"{request.remote_addr} - - '{request.method} {request.path}' {response.status_code} | Error Occured"
            )

        self.info(
            f"{request.remote_addr} - - '{request.method} {request.path}' {response.status_code} | Response Completed",
        )
        self.custom_info(
            {
                "request_id": request.id,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": self.get_response_body(response),
            },
        )

    def get_request_id(self, request):
        """Generate request id"""
        id = request.headers.get("X-Request-ID") if not hasattr(request, "id") else request.id

        if not id:
            id = str(uuid4())
        
        request.id = id

    def get_request_body(self, request):
        content_type = request.headers.get("Content-Type", "")
        
        if "application/json" in content_type and request.is_json:
            body = request.json
        elif "application/x-www-form-urlencoded" in content_type:
            body = request.files
        elif "multipart/form-data" in content_type:
            body = {
                "files": [
                    {"name": file.filename, "type": file.content_type}
                    for file in request.files.values()
                ],
                "form": request.form,
            }
        elif "text/html" in content_type:
            body = request.data.decode("utf-8")
        else:
            body = {
                "data": request.data.decode("utf-8"),
            }

        return body

    def get_response_body(self, response):
        """Get response body"""
        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            return response.json
        else:
            return response.data.decode("utf-8")
    
    def __setup_handlers(self, level: int, formatter: logging.Formatter):
        """Setup handlers"""
        # File handler
        # create file if not exists
        os.makedirs(self.dir, exist_ok=True)

        # Info file handler
        file_handler = logging.FileHandler(self.info_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        # Error file handler
        error_file_handler = logging.FileHandler(self.error_file)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)

        # Console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(handler)