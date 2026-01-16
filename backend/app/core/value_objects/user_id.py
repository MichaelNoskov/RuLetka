from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserID:
    value: Optional[int] = None
    
    def __post_init__(self):
        if self.value is not None and self.value <= 0:
            raise ValueError("User ID must be positive")
    
    def is_persisted(self) -> bool:
        return self.value is not None
    
    def __str__(self) -> str:
        return str(self.value) if self.value else "new"
