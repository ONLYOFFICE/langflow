from .base import BaseClient
from .services import DealService


class Client(BaseClient):
    def __init__(self):
        self.deals = DealService(self)
