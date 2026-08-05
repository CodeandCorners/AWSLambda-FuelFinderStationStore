from models.FuelStationDBDataClasses import FuelStation



def saveFuelStations(
    stations: list[FuelStation],
    dynamoDb
) -> None:
    print(f"inserting {len(stations)} Fuel stations into fuel-stations")
    with dynamoDb.Table("fuel-stations").batch_writer() as batch:
        for station in stations:
            batch.put_item(
                Item={
                    "id": station.id,
                    "name": station.name,
                    "createdAt": station.createdAt,
                    "ttl": station.ttl,
                    "geohash": station.geohash,
                    "location": {
                        "addressLine1": station.location.address_line_1,
                        "postcode": station.location.postcode,
                        "latitude": station.location.latitude,
                        "longitude": station.location.longitude
                    },
                    "openingTimes": {
                        "monday": vars(station.openingTimes.monday),
                        "tuesday": vars(station.openingTimes.tuesday),
                        "wednesday": vars(station.openingTimes.wednesday),
                        "thursday": vars(station.openingTimes.thursday),
                        "friday": vars(station.openingTimes.friday),
                        "saturday": vars(station.openingTimes.saturday),
                        "sunday": vars(station.openingTimes.sunday),
                    }
                }
            )