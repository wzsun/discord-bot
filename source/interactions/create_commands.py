import requests
from config import secrets

url = (
    "https://discord.com/api/v8/applications/{discord_application_id}/commands".format(
        discord_application_id=secrets.secret_discord_application_id
    )
)

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "list-timer",
    "type": 1,
    "description": "Shows afk timer of a user",
    "options": [
        {
            "name": "user",
            "description": "User used for afk timer",
            "type": 6,
            "required": True,
        },
    ],
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot {discord_bot_token}".format(
        discord_bot_token=secrets.secret_discord_bot_token
    )
}

r = requests.post(url, headers=headers, json=json)
