from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class LoginUserUseCase(ABC):
    @abstractmethod
    async def execute(self, username: str, password: str) -> dict[str, Any]:
        pass


class RegisterUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        username: str,
        password: str,
        is_male: bool,
        birthdate: date,
        country: str,
        description: str = ""
    ) -> dict[str, Any]:
        pass
