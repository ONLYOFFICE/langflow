from __future__ import annotations

from typing import Self

from .base import Client as Base
from .base import Opener
from .services import AuthService, FilesService, PortalService
from .transformers import AuthTokenTransformer, OriginTransformer


class Client(Base):
    def __init__(self, opener: Opener | None = None):
        super().__init__(opener)
        self.auth = AuthService(self)
        self.files = FilesService(self)
        self.portal = PortalService(self)


    def with_auth_token(self, token: str) -> Self:
        transformer = AuthTokenTransformer(token)
        return self._with_transformer(transformer)


    def with_origin(self, origin: str) -> Self:
        transformer = OriginTransformer(origin)
        return self._with_transformer(transformer)
