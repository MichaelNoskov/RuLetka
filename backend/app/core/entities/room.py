from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Room:
    id: str
    client_ids: List[str]
    created_at: datetime
    is_active: bool = True
    gender_filter: Optional[str] = None
    age_filter: Optional[int] = None
    country_filter: Optional[str] = None
