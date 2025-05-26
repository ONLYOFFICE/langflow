from .base import BaseClient
from .services import ActivityService, DealService, LeadService, NoteService, PersonService


class Client(BaseClient):
    def __init__(self):
        self.activities = ActivityService(self)
        self.deals = DealService(self)
        self.leads = LeadService(self)
        self.persons = PersonService(self)
        self.notes = NoteService(self)
