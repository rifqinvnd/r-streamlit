class CommonError(Exception):
    """Base class for all common errors."""
    def __init__(self, message = "", status_code = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class BadRequest(CommonError):
    """Exception raised for bad requests."""
    def __init__(self, message = "Bad request"):
        super().__init__(message, status_code=400)

class Unauthorized(CommonError):
    """Exception raised for authorization errors."""
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=401)

class NotFound(CommonError):
    """Exception raised for not found errors."""
    def __init__(self, message = "Not found"):
        super().__init__(message, status_code=404)

class NotImplemented(CommonError):
    """Exception raised for not implemented errors."""
    def __init__(self, message = "Not implemented"):
        super().__init__(message, status_code=501)
