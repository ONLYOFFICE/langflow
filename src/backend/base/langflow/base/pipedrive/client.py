from .base import BaseClient
from .services import (
    ActivityService,
    DealService,
    LeadService,
    NoteService,
    OrganizationService,
    PersonService,
    UserService,
)


class Client(BaseClient):
    def __init__(self):
        self.activities = ActivityService(self)
        self.deals = DealService(self)
        self.leads = LeadService(self)
        self.notes = NoteService(self)
        self.organizations = OrganizationService(self)
        self.persons = PersonService(self)
        self.users = UserService(self)
