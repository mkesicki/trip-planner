from dataclasses import dataclass
from typing import Optional

@dataclass
class TransportDetails:
    transport_type: str
    pickup_place: Optional[str] = None
    return_place: Optional[str] = None
