from .base import BaseClient
from .services import AuthService, UsersService


class Client(BaseClient):
    def __init__(self):
        self.auth = AuthService(self)
        self.users = UsersService(self)
