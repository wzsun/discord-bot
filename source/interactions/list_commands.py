import requests
from config import secrets

url = "https://discord.com/api/v8/applications/{discord_application_id}/commands".format(discord_application_id=secrets.secret_discord_application_id)
# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot {discord_bot_token}".format(discord_bot_token=secrets.secret_discord_bot_token)
}

r = requests.get(url, headers=headers)
print(r.text)