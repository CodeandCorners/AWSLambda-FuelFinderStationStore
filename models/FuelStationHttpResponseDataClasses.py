from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FuelStationLocationResponse:
    address_line_1: str
    postcode: str
    latitude: Decimal
    longitude: Decimal

@dataclass
class OpeningTimeResponse:
    open: str
    close: str
    is_24_hours: bool

@dataclass
class OpeningTimesResponse:
    monday: OpeningTimeResponse
    tuesday: OpeningTimeResponse
    wednesday: OpeningTimeResponse
    thursday: OpeningTimeResponse
    friday: OpeningTimeResponse
    saturday: OpeningTimeResponse
    sunday: OpeningTimeResponse


@dataclass
class FuelStationResponse:
    node_id: str
    trading_name: str
    brand_name: str
    is_same_trading_and_brand_name: bool
    temporary_closure: bool
    permanent_closure: bool
    location: FuelStationLocationResponse
    openingTimes: OpeningTimesResponse