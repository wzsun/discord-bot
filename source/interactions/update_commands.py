import requests
from config import secrets

url = "https://discord.com/api/v8/applications/{discord_application_id}/commands/{discord_command_id}".format(
    discord_application_id=secrets.secret_discord_application_id,
    discord_command_id=secrets.discord_command_id,
)

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "timer",
    "type": 1,
    "description": "afk timer actions for a user",
    "options": [
        {
            "name": "user",
            "description": "User used for afk timer",
            "type": 6,
            "required": True,
        },
        {
            "name": "action",
            "description": "Start or stop afk timer",
            "required": True,
            "choices": [
                {
                    "name": "Start",
                    "value": "true",
                },
                {
                    "name": "Stop",
                    "value": "false",
                },
            ],
            "type": 3,
        },
    ],
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot {discord_bot_token}".format(
        discord_bot_token=secrets.secret_discord_bot_token
    )
}

r = requests.patch(url, headers=headers, json=json)
