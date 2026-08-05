## What
Lambda to update fuel stations from gov uk API, hypothetically once a day,

API Response models from fuel finder last checked 5th August 2026

Please Note, This repo has been setup to share Auth Secret + Auth Dynamo DB table with https://github.com/CodeandCorners/AWSLambda-FuelFinderPriceStore

Creation of these entities only needs to happen once, Inline policies will have to be set per lambda


## How to
- create one login dev account
- setup application for fuel finder api
- grab client id and secret
- setup AWS secret "govUKfuelFinderOAuthSecret"
{
  "client_secret": "the secret from gov uk dev portal",
  "client_id": "the client id from uk dev portal"
}
- set up lambda in AWS
- create inline policy to point lamda at secret (get secret ARN to use in policy) something like this, but not exactly
```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "ReadFuelFinderSecret",
			"Effect": "Allow",
			"Action": "secretsmanager:GetSecretValue",
			"Resource": "ARN OF SECRET HERE"
		}
	]
}
```
- create dynamoDb table, called "api-tokens"
- turn on TTL, for field "ttl"
- Add inline policy on lambda, just something like this but not exactly
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "FuelFinderTokenCache",
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem"
            ],
            "Resource": "ARN of TABLE HERE"
        }
    ]
}
```


- geohash2 dependency for local

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

- geohash2 dependency for lambda

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt -t package/`

- pull geohash2 main folder out package and place folder in top level (same level as lambda_function.py)
- REMOVE .venv file other wise you won't be able to push to AWS



## Notable config