from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import threading
import time
import os
import httpx
import asyncio
import requests

from openai import AzureOpenAI

from detector import CameraMotionDetector, recorded_videos_queue, lock
from status import functioning as global_functioning, previous_functioning

# === Load environment variables ===
load_dotenv()

# === Azure OpenAI Setup ===
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=AZURE_API_VERSION
)

# === FastAPI App ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with allowed domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Globals ===
VIDEO_DIR = "recordings"
expo_push_tokens = set()
event_loop = asyncio.get_event_loop()

# === Request Models ===
class NotificationPayload(BaseModel):
    title: str
    body: str

class Message(BaseModel):
    message: str

# === Internal Functions ===
def send_push_notification(token, title, body):
    message = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body,
    }
    response = requests.post(
        "https://exp.host/--/api/v2/push/send",
        json=message,
        headers={"Content-Type": "application/json"},
    )
    print(f"📨 Sent notification to {token}: {response.status_code}")

def get_machine_status():
    return {"status": "Running"}

def get_activity_log():
    return {
        "Log": """Machine 1: Stopped Tuesday 11:30 AM
Machine 1: Started working again Tuesday 3:30 PM
Machine 3: Stopped Tuesday 11:30 AM
Machine 2: Stopped Tuesday 11:30 AM"""
    }

# === ROUTES ===

@app.post("/internal-update-status")
async def update_status(request: Request):
    data = await request.json()
    new_status = data.get("functioning")
    print("🔄 Updating status from internal request")

    global global_functioning, previous_functioning

    temp_token = "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
    if new_status:
        send_push_notification(temp_token, "✅ Production Running", "Production line is functioning normally!")
    else:
        send_push_notification(temp_token, "⛔ Stoppage Detected", "Production line has stopped!")

    return {"message": "Status updated"}

@app.get("/videos/{filename}")
def get_video(filename: str):
    file_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path=file_path, media_type='video/mp4')

@app.post("/send-notification")
async def send_notification(payload: NotificationPayload):
    temp_token = "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
    send_push_notification(temp_token, payload.title, payload.body)
    return {"message": "Notification sent"}

@app.post("/register-token")
async def register_token(request: Request):
    data = await request.json()
    token = data.get("token")
    if token:
        expo_push_tokens.add(token)
        print(f"✅ Token registered: {token}")
        return {"message": "Token registered"}
    return {"message": "No token provided"}

@app.get("/new-videos")
def get_new_videos():
    with lock:
        videos = list(recorded_videos_queue)
        recorded_videos_queue.clear()
    return {"new_videos": [os.path.basename(v) for v in videos]}

@app.get("/status")
def get_status():
    return {"status": "Running" if global_functioning else "Stopped"}

@app.post("/chat")
async def chat_with_openai(msg: Message):
    user_message = msg.message

    functions = [
        {
            "name": "get_machine_status",
            "description": "Check if the machine is running",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_activity_log",
            "description": "Get the activity log of the machine",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]

    messages = [{"role": "user", "content": user_message}]

    try:
        # Initial response with potential function call
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=messages,
            functions=functions,
            function_call="auto"
        )

        response_message = response.choices[0].message

        if response_message.function_call:
            function_response = None
            fn_name = response_message.function_call.name

            if fn_name == "get_machine_status":
                function_response = get_machine_status()
            elif fn_name == "get_activity_log":
                function_response = get_activity_log()

            messages.append(response_message)
            messages.append({
                "role": "function",
                "name": fn_name,
                "content": str(function_response)
            })

            final_response = client.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=messages
            )

            return {"reply": final_response.choices[0].message.content}

        return {"reply": response_message.content}

    except Exception as e:
        return {"error": f"OpenAI error: {str(e)}"}
