from app.services.DatabaseService import DatabaseService


class AuthenticationService:
    def __init__(self):
        self.database_service = DatabaseService()

    def authenticate(self, username: str, password: str):
        user_data = self.database_service.get_user_data(username=username)
        
        if (
            username == user_data.get("username", "")
            and password == user_data.get("password", "")
        ):
            return True

        return False
