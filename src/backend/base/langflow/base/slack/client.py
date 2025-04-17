from .base import BaseClient
from .services import ChatService, ConversationService


class Client(BaseClient):
    def __init__(self):
        self.auth = None
        self.chat = ChatService(self)
        self.conversation = ConversationService(self)
