from models.FuelAuthDataClasses import BearerTokenResponse
import urllib3
import json
from typing import List
from models.FuelStationHttpResponseDataClasses import FuelStationResponse, FuelStationLocationResponse, OpeningTimeResponse, OpeningTimesResponse
from decimal import Decimal

# Example from https://www.developer.fuel-finder.service.gov.uk/fuel-finder/apis-ifr/info-recipent/docs?operationId=getPFSInfo
# Fields here https://www.developer.fuel-finder.service.gov.uk/fuel-finder/api-guide
# [
# {
# "node_id": "9b275ab576eeba3c6677984be15ee22a74e54fdfe8e5ea700e84a03178dc4ac1",
# "public_phone_number": null,
# "trading_name": "TEST",
# "is_same_trading_and_brand_name": true,
# "brand_name": "TEST",
# "temporary_closure": false,
# "permanent_closure": false,
# "permanent_closure_date": null,
# "is_motorway_service_station": false,
# "is_supermarket_service_station": false,
# "location": {
# "address_line_1": "HALL & WOODHOUSE, TAPLOW BOATYARD, MILL LANE, TAPLOW, MAIDENHEAD, SL6 0AA",
# "address_line_2": null,
# "city": "MAIDENHEAD",
# "country": "England",
# "county": null,
# "postcode": "SL6 0AA",
# "latitude": 51.5268585,
# "longitude": -0.700361
# },
# "amenities": [
# "water_filling"
# ],
# "opening_times": {
# "usual_days": {
# "monday": {
# "open": "00:00:00",
# "close": "00:00:00",
# "is_24_hours": false
# },
# "tuesday": {
# "open": "00:00:00",
# "close": "00:00:00",
# "is_24_hours": false
# },
# "wednesday": {
# "open": "00:00:00",
# "close": "00:00:00",
# "is_24_hours": false
# },
# "thursday": {
# "open": "00:00:00",
# "close": "00:00:00",
# "is_24_hours": false
# },
# "friday": {
# "open": "00:00:00",
# "close": "00:00:00",
# "is_24_hours": false
# },
# "saturday": {
# "open": "00:00:00",
# "close": "00:00:00",
# "is_24_hours": false
# },
# "sunday": {
# "open": "00:00:00",
# "close": "23:59:00",
# "is_24_hours": true
# }
# },
# "bank_holiday": {
# "type": "bank holiday",
# "open_time": "00:00:00",
# "close_time": "00:00:00",
# "is_24_hours": false
# }
# },
# "fuel_types": [
# "E10",
# "E5",
# "HVO",
# "B10"
# ]
# }]

def getFuelStations(bearerToken: BearerTokenResponse, http: urllib3.PoolManager, batchNumber: int) -> List[FuelStationResponse]:
    fuelStationResponse = http.request(
        "GET",
        f"https://www.fuel-finder.service.gov.uk/api/v1/pfs?batch-number={batchNumber}",
        headers={
            "Authorization": f"Bearer {bearerToken.bearerToken}"
        }
    )
    if (fuelStationResponse.status == 404):
        print(f"Fuel Station request returned 404, Assumed no more data available for batch number {batchNumber}")
        return []
    elif (fuelStationResponse.status != 200):
        raise Exception(
            f"Fuel price request failed: {fuelStationResponse.status}"
        )
    else:
        print(f"Fuel price request returned {fuelStationResponse.status}, continuing to process data for batch number {batchNumber}")
        jsonResponse = json.loads(fuelStationResponse.data.decode("utf-8"))


        return [
            createFuelStation(station)
        for station in jsonResponse
        ]

def createFuelStation(data: dict) -> FuelStationResponse:
    days = data["opening_times"]["usual_days"]

    return FuelStationResponse(
        node_id=data["node_id"],
        trading_name=data["trading_name"],
        brand_name=data.get("brand_name"),
        is_same_trading_and_brand_name=data["is_same_trading_and_brand_name"],
        temporary_closure=data["temporary_closure"],
        permanent_closure=data.get("permanent_closure"),

        location=FuelStationLocationResponse(
            address_line_1=data["location"]["address_line_1"],
            postcode=data["location"]["postcode"],
            latitude=Decimal(str(data["location"]["latitude"])),
            longitude=Decimal(str(data["location"]["longitude"]))
        ),

        openingTimes=OpeningTimesResponse(
            monday=OpeningTimeResponse(**days["monday"]),
            tuesday=OpeningTimeResponse(**days["tuesday"]),
            wednesday=OpeningTimeResponse(**days["wednesday"]),
            thursday=OpeningTimeResponse(**days["thursday"]),
            friday=OpeningTimeResponse(**days["friday"]),
            saturday=OpeningTimeResponse(**days["saturday"]),
            sunday=OpeningTimeResponse(**days["sunday"])
        )
        )