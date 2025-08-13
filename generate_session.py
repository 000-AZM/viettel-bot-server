# generate_session.py - run locally to create USERBOT_SESSION
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print(">>> Get API_ID and API_HASH from https://my.telegram.org/apps")
API_ID = int(input("API_ID: ").strip())
API_HASH = input("API_HASH: ").strip()

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
  print(">>> Log in with your phone...")
  string = client.session.save()
  print("\n=== YOUR USERBOT_SESSION (keep secret) ===")
  print(string)
  print("==========================================")
