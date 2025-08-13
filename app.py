# app.py - FastAPI + Telethon userbot service
import os, asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import UsernameInvalidError, UsernameNotOccupiedError, FloodWaitError, AuthKeyUnregisteredError
import uvicorn

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
USERBOT_SESSION = os.environ.get("USERBOT_SESSION", "")  # Telethon StringSession of your user account

if not API_ID or not API_HASH or not USERBOT_SESSION:
  raise RuntimeError("Missing API_ID/API_HASH/USERBOT_SESSION env vars")

client = TelegramClient(StringSession(USERBOT_SESSION), API_ID, API_HASH)
app = FastAPI(title="Userbot Service")

class FetchPayload(BaseModel):
  bot_username: str
  command: str

@app.on_event("startup")
async def startup_event():
  await client.connect()
  if not await client.is_user_authorized():
    raise RuntimeError("User session not authorized. Regenerate USERBOT_SESSION.")

@app.on_event("shutdown")
async def shutdown_event():
  await client.disconnect()

@app.post("/fetch")
async def fetch(payload: FetchPayload):
  bot_username = payload.bot_username.strip()
  command = payload.command.strip()
  try:
    # Use conversation to send a command and wait for the bot's reply
    async with client.conversation(bot_username, timeout=45) as conv:
      await conv.send_message(command)
      resp = await conv.get_response()
      text = resp.message if hasattr(resp, 'message') else (resp.text if hasattr(resp, 'text') else str(resp))
      return {"ok": True, "text": text, "raw": {"id": resp.id, "date": str(resp.date)}}
  except FloodWaitError as e:
    raise HTTPException(status_code=429, detail=f"Flood wait: {e.seconds}s")
  except (UsernameInvalidError, UsernameNotOccupiedError):
    raise HTTPException(status_code=400, detail="Invalid bot username")
  except asyncio.TimeoutError:
    raise HTTPException(status_code=504, detail="No response from bot (timeout)")
  except AuthKeyUnregisteredError:
    raise HTTPException(status_code=500, detail="User session expired. Regenerate USERBOT_SESSION.")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), reload=False)
