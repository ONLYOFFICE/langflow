from .base import BaseClient
from .services import AuthService, MeetingService, UsersService


class Client(BaseClient):
    def __init__(self):
        self.auth = AuthService(self)
        self.meetings = MeetingService(self)
        self.users = UsersService(self)
