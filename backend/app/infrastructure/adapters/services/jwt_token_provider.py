from jose import jwt
from typing import Dict

from app.core.ports.services.token_provider import AbstractTokenProvider


class JWTTokenProvider(AbstractTokenProvider):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create(self, user_id: str) -> str:
        return jwt.encode(
            {"sub": str(user_id)},
            self.secret_key,
            algorithm=self.algorithm
        )

    def verify(self, token: str) -> Dict:
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]
        )
