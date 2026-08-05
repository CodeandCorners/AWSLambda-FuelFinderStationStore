import json
import boto3
from connectors.FuelFinderOAuthConnector import getFuelFinderOAuthAccessToken
from connectors.FuelStationConnector import getFuelStations
from db.TokenDB import getAccessToken, saveAccessToken
from models.FuelAuthDataClasses import BearerTokenResponse
from models.FuelStationDBDataClasses import createFuelStationFromResponse
import urllib3

#http
secrets = boto3.client("secretsmanager")
http = urllib3.PoolManager()

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


def fuelStationOrchestration(bearerToken: BearerTokenResponse):
        response = getFuelStations(bearerToken, http, 1)
        converted = createFuelStationFromResponse(response[0],1,5)
        print(converted)

def lambda_handler(event, context):
    fuelFinderBearerToken = retrieveOrSaveBearerToken()
    fuelStationOrchestration(fuelFinderBearerToken)
    
    return "Updated fuel-stations table"
