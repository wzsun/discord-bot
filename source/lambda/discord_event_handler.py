import json
import boto3
import base64
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from botocore.exceptions import ClientError
import time

PING_PONG = {"type": 1}
RESPONSE_TYPES = {
    "PONG": 1,
    "CHANNEL_MESSAGE_WITH_SOURCE": 4,
    "DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE": 5,
    "DEFERRED_UPDATE_MESSAGE": 6,
    "UPDATE_MESSAGE": 7,
    "APPLICATION_COMMAND_AUTOCOMPLETE_RESULT": 8,
}

# human readable name to id for discord interactions
MY_DISCORD_ACTIONS = {
    "start-stop-timer": "",
    "list-timer": "",
}


def get_secret():
    secret_name = (
        ""
    )
    region_name = ""

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            # Please see https://docs.aws.amazon.com/secretsmanager/latest/apireference/CommonErrors.html for all the other types of errors not handled above
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            return get_secret_value_response["SecretString"]
        else:
            return base64.b64decode(get_secret_value_response["SecretBinary"])


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event["params"]["header"].get("x-signature-ed25519")
    auth_ts = event["params"]["header"].get("x-signature-timestamp")

    message = auth_ts.encode() + raw_body.encode()
    discord_public_key = json.loads(get_secret())["Discord Bot Public Key"]
    verify_key = VerifyKey(bytes.fromhex(discord_public_key))
    verify_key.verify(message, bytes.fromhex(auth_sig))  # raises an error if unequal


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def lambda_handler(event, context):
    # print(f"event {event}") # debug print
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # check if message is a ping
    body = event.get("body-json")
    if ping_pong(body):
        return PING_PONG

    # check what event is coming from discord
    eventType = event["body-json"]["data"]["id"]
    timedUserId = event["body-json"]["data"]["options"][0]["value"]
    userName = event["body-json"]["data"]["resolved"]["users"][timedUserId]["username"]

    if eventType == MY_DISCORD_ACTIONS["start-stop-timer"]:
        isItStartingATimer = event["body-json"]["data"]["options"][1]["value"]
        pointOfTime = int(time.time())
        db = boto3.client("dynamodb")
        # better way to do this?
        table_data = db.get_item(
            TableName="discord_afk_timer", Key={"user_id": {"S": timedUserId}}
        )
        existingStartTime = ""
        existingTimeInSeconds = 0
        if "Item" in table_data:
            existingStartTime = table_data["Item"]["start_timer"]["S"]
            existingTimeInSeconds = table_data["Item"]["timeInSeconds"]["N"]

        if isItStartingATimer == "true":
            # if an existing start time is present, we bail out
            if len(existingStartTime) > 0:
                return {
                    "type": RESPONSE_TYPES["CHANNEL_MESSAGE_WITH_SOURCE"],
                    "data": {
                        "tts": False,
                        "content": "Timer has already started",
                        "embeds": [],
                        "allowed_mentions": [],
                    },
                }

            data = db.put_item(
                TableName="discord_afk_timer",
                Item={
                    "user_id": {"S": timedUserId},
                    "timeInSeconds": {"N": str(existingTimeInSeconds)},
                    "start_timer": {"S": str(pointOfTime)},
                },
            )

            return {
                "type": RESPONSE_TYPES["CHANNEL_MESSAGE_WITH_SOURCE"],
                "data": {
                    "tts": False,
                    "content": "Timer has started for {discord_user}".format(
                        discord_user=userName
                    ),
                    "embeds": [],
                    "allowed_mentions": [],
                },
            }
        else:
            if len(existingStartTime) == 0:
                return {
                    "type": RESPONSE_TYPES["CHANNEL_MESSAGE_WITH_SOURCE"],
                    "data": {
                        "tts": False,
                        "content": "Timer hasn't started, try starting the timer",
                        "embeds": [],
                        "allowed_mentions": [],
                    },
                }

            updatedTime = str(
                (pointOfTime - int(existingStartTime))
                + int(table_data["Item"]["timeInSeconds"]["N"])
            )
            data = db.put_item(
                TableName="discord_afk_timer",
                Item={
                    "user_id": {"S": timedUserId},
                    "timeInSeconds": {"N": updatedTime},
                    "start_timer": {"S": ""},
                },
            )
            return {
                "type": RESPONSE_TYPES["CHANNEL_MESSAGE_WITH_SOURCE"],
                "data": {
                    "tts": False,
                    "content": "Total wasted time waiting for {discord_user}: {wasted_time} seconds".format(
                        discord_user=userName, wasted_time=updatedTime
                    ),
                    "embeds": [],
                    "allowed_mentions": [],
                },
            }

    if eventType == MY_DISCORD_ACTIONS["list-timer"]:
        db = boto3.client("dynamodb")
        table_data = db.get_item(
            TableName="discord_afk_timer", Key={"user_id": {"S": timedUserId}}
        )
        wastedTime = "0"
        if "Item" in table_data:
            wastedTime = table_data["Item"]["timeInSeconds"]["N"]

        return {
            "type": RESPONSE_TYPES["CHANNEL_MESSAGE_WITH_SOURCE"],
            "data": {
                "tts": False,
                "content": "Total wasted time waiting for {discord_user}: {wasted_time} seconds".format(
                    discord_user=userName, wasted_time=wastedTime
                ),
                "embeds": [],
                "allowed_mentions": [],
            },
        }

    return {
        "type": RESPONSE_TYPES["CHANNEL_MESSAGE_WITH_SOURCE"],
        "data": {
            "tts": False,
            "content": "not sure how we got here ...",
            "embeds": [],
            "allowed_mentions": [],
        },
    }
