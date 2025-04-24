from .base import BaseClient
from .services import AuthService


class Client(BaseClient):
    def __init__(self):
        self.auth = AuthService(self)
