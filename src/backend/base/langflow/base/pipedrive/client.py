from .base import BaseClient
from .services import ActivityService, DealService


class Client(BaseClient):
    def __init__(self):
        self.activities = ActivityService(self)
        self.deals = DealService(self)
