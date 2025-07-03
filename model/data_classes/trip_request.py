from dataclasses import dataclass, field
from typing import List
from .transport_details import TransportDetails
from .accommodation_details import AccommodationDetails

@dataclass
class TripRequest:
    from_country: str
    to_country: str
    from_city: str
    start_date: str
    end_date: str
    back_time: str
    adults: int
    round_trip: bool
    hotels_only: bool
    transport_only: bool
    transport_start: TransportDetails
    transport_end: TransportDetails
    places: List[AccommodationDetails] = field(default_factory=list)
