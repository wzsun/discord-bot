import requests
from config import secrets

url = "https://discord.com/api/v8/applications/{discord_application_id}/commands".format(discord_application_id=secrets.secret_discord_application_id)

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "blep",
    "type": 1,
    "description": "Send a random adorable animal photo",
    "options": [
        {
            "name": "animal",
            "description": "The type of animal",
            "type": 3,
            "required": True,
            "choices": [
                {
                    "name": "Dog",
                    "value": "animal_dog"
                },
                {
                    "name": "Cat",
                    "value": "animal_cat"
                },
                {
                    "name": "Penguin",
                    "value": "animal_penguin"
                }
            ]
        },
        {
            "name": "only_smol",
            "description": "Whether to show only baby animals",
            "type": 5,
            "required": False
        }
    ]
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot {discord_bot_token}".format(discord_bot_token=secrets.secret_discord_bot_token)
}

r = requests.post(url, headers=headers, json=json)