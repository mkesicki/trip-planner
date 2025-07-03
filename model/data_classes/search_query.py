from dataclasses import dataclass
from typing import Optional
import datetime

@dataclass
class SearchQuery:
    from_city: str
    from_country: str
    to_city: str
    to_country: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    adults: int
    round_trip: bool
    params: dict
    pickup_place: Optional[str] = None
    return_place: Optional[str] = None
