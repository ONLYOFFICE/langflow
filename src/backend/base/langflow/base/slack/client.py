from .base import BaseClient
from .services import ChatService, ConversationService, PinService, UserService


class Client(BaseClient):
    def __init__(self):
        self.auth = None
        self.chat = ChatService(self)
        self.conversation = ConversationService(self)
        self.pin = PinService(self)
        self.user = UserService(self)
