class AuthenticationService:
    def __init__(self):
        self.database_service = ""

    def authenticate(self, username: str, password: str):
        login_info = self.database_service.get_user_login_info(
            username=username,
            password=password,
        )

        if login_info:
            return True
        
        return False
