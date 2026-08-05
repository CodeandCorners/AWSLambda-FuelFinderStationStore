import json
import boto3
from connectors.FuelFinderOAuthConnector import getFuelFinderOAuthAccessToken
from connectors.FuelStationConnector import getFuelStations
from db.TokenDB import getAccessToken, saveAccessToken
from models.FuelStationHttpResponseDataClasses import FuelStationResponse
from models.FuelAuthDataClasses import BearerTokenResponse
from models.FuelStationDBDataClasses import createFuelStationFromResponse, FuelStation
import urllib3
from db.FuelStationDB import saveFuelStations
from datetime import datetime, timedelta

#http
secrets = boto3.client("secretsmanager")
http = urllib3.PoolManager()
maxBatchNumberForFuelStationsApi = 99

#db
tokenTTLInSeconds = 1800
dynamodb = boto3.resource("dynamodb")

# 5 = ~5km
fuelStationGeoHashPrecision = 5

def getOAuthSecretsForFuelFinderApi() -> dict[str, str]:
    response = secrets.get_secret_value(
        SecretId="govUKfuelFinderOAuthSecret"
    )

    return json.loads(response["SecretString"])

def retrieveOrSaveBearerToken() -> BearerTokenResponse:
    accessToken = getAccessToken(dynamodb)
    if accessToken is not None:
        print("Access token found in DB, no API call needed")
        return BearerTokenResponse(accessToken)
    else:
        print("No access token found in DB, making API call")
        secret = getOAuthSecretsForFuelFinderApi()
        clientId = secret["client_id"]
        clientSecret = secret["client_secret"]
        fuelFinderBearerToken: BearerTokenResponse = getFuelFinderOAuthAccessToken(clientId, clientSecret, http)
        
        saveAccessToken(fuelFinderBearerToken.bearerToken, tokenTTLInSeconds, dynamodb)
        return fuelFinderBearerToken


def fuelStationGetAndInsert(bearerToken: BearerTokenResponse, batchNumber: int, createdAt: int, ttl: int) -> bool:
    fuelStationData: list[FuelStationResponse] = getFuelStations(bearerToken, http, batchNumber)

    if len(fuelStationData) > 0:
        convertedData: list[FuelStation | None] = [
            createFuelStationFromResponse(station, createdAt, ttl, fuelStationGeoHashPrecision)
            for station in fuelStationData
        ]

        saveFuelStations(list(filter(None, convertedData)), dynamodb)
    print(f"Fuel stations found {len(fuelStationData)}")
    
    return len(fuelStationData) > 0

def fuelStationOrchestration(bearerToken: BearerTokenResponse):
    now = datetime.now()
    dateTimeNow: int = int(now.timestamp())
    ttlOfDataRetrieved: int = int((now + timedelta(days=7)).timestamp())
 
    batchNumber = 1
    while batchNumber <= maxBatchNumberForFuelStationsApi:
        print(f"Processing batch number {batchNumber}")
        hasDataInBatch: bool = fuelStationGetAndInsert(bearerToken, batchNumber, dateTimeNow, ttlOfDataRetrieved)
        if not hasDataInBatch:
            print(f"No data returned for batch number {batchNumber}, stopping processing")
            break
        batchNumber += 1

def lambda_handler(event, context):
    fuelFinderBearerToken = retrieveOrSaveBearerToken()
    fuelStationOrchestration(fuelFinderBearerToken)
    
    return "Updated fuel-stations table"
