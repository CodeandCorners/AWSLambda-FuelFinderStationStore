from dataclasses import dataclass
from decimal import Decimal
from models.FuelStationHttpResponseDataClasses import FuelStationResponse
import geohash2

@dataclass
class FuelStationLocation:
    address_line_1: str
    postcode: str
    latitude: Decimal
    longitude: Decimal

@dataclass
class OpeningTime:
    open: str
    close: str
    is_24_hours: bool

@dataclass
class OpeningTimes:
    monday: OpeningTime
    tuesday: OpeningTime
    wednesday: OpeningTime
    thursday: OpeningTime
    friday: OpeningTime
    saturday: OpeningTime
    sunday: OpeningTime


@dataclass
class FuelStation:
    id: str
    name: str
    location: FuelStationLocation
    geohash: str
    openingTimes: OpeningTimes
    ttl: int
    createdAt: int
    

def returnName(tradingName: str, brandName: str, same: bool) -> str:
    if(same):
        return brandName
    else:
        return f"{brandName} {tradingName}"

def createFuelStationFromResponse(
    fuelStationResponse: FuelStationResponse,
    createdAt: int,
    ttl: int,
    geoHashPrecison: int
    ) -> FuelStation | None:

    if fuelStationResponse.permanent_closure or fuelStationResponse.temporary_closure:
        print(
            f"Fuel station {fuelStationResponse.brand_name} "
            f"has declared to be closed, not adding to DB"
        )
        return None

    name = returnName(
        fuelStationResponse.trading_name,
        fuelStationResponse.brand_name,
        fuelStationResponse.is_same_trading_and_brand_name
    )
    geohash=geohash2.encode(
                float(fuelStationResponse.location.latitude),
                float(fuelStationResponse.location.longitude),
                precision=geoHashPrecison
            )
    

    location = FuelStationLocation(
        address_line_1=fuelStationResponse.location.address_line_1,
        postcode=fuelStationResponse.location.postcode,
        latitude=fuelStationResponse.location.latitude,
        longitude=fuelStationResponse.location.longitude,
    )

    opening_times = OpeningTimes(
        monday=OpeningTime(
            open=fuelStationResponse.openingTimes.monday.open,
            close=fuelStationResponse.openingTimes.monday.close,
            is_24_hours=fuelStationResponse.openingTimes.monday.is_24_hours
        ),
        tuesday=OpeningTime(
            open=fuelStationResponse.openingTimes.tuesday.open,
            close=fuelStationResponse.openingTimes.tuesday.close,
            is_24_hours=fuelStationResponse.openingTimes.tuesday.is_24_hours
        ),
        wednesday=OpeningTime(
            open=fuelStationResponse.openingTimes.wednesday.open,
            close=fuelStationResponse.openingTimes.wednesday.close,
            is_24_hours=fuelStationResponse.openingTimes.wednesday.is_24_hours
        ),
        thursday=OpeningTime(
            open=fuelStationResponse.openingTimes.thursday.open,
            close=fuelStationResponse.openingTimes.thursday.close,
            is_24_hours=fuelStationResponse.openingTimes.thursday.is_24_hours
        ),
        friday=OpeningTime(
            open=fuelStationResponse.openingTimes.friday.open,
            close=fuelStationResponse.openingTimes.friday.close,
            is_24_hours=fuelStationResponse.openingTimes.friday.is_24_hours
        ),
        saturday=OpeningTime(
            open=fuelStationResponse.openingTimes.saturday.open,
            close=fuelStationResponse.openingTimes.saturday.close,
            is_24_hours=fuelStationResponse.openingTimes.saturday.is_24_hours
        ),
        sunday=OpeningTime(
            open=fuelStationResponse.openingTimes.sunday.open,
            close=fuelStationResponse.openingTimes.sunday.close,
            is_24_hours=fuelStationResponse.openingTimes.sunday.is_24_hours
        )
    )

    return FuelStation(
        id=fuelStationResponse.node_id,
        name=name,
        location=location,
        geohash=geohash,
        openingTimes=opening_times,
        ttl=ttl,
        createdAt=createdAt
    )