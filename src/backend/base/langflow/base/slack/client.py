from .base import BaseClient
from .services import ChatService


class Client(BaseClient):
    def __init__(self):
        self.auth = None
        self.chat = ChatService(self)
