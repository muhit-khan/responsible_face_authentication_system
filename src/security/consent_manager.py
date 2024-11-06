from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class ConsentRecord:
    """Track user consent and data usage permissions."""
    user_id: str
    consent_date: datetime
    purpose: str
    retention_period: int  # in days
    data_types: List[str]
    revoked: bool = False