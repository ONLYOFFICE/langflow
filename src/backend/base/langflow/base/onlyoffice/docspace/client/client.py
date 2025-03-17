from __future__ import annotations
from typing import Self
from .base import Client as Base, Opener
from .services import AuthService, FilesService
from .transformers import AuthTokenTransformer


class Client(Base):
    def __init__(self, opener: Opener | None = None):
        super().__init__(opener)
        self.auth = AuthService(self)
        self.files = FilesService(self)


    def with_auth_token(self, token: str) -> Self:
        transformer = AuthTokenTransformer(token)
        return self._with_transformer(transformer)
