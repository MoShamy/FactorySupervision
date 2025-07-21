from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import os
import httpx
import asyncio
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi import HTTPException
from notifications import send_push_notification, expo_push_tokens
import requests
from detector import CameraMotionDetector, recorded_videos_queue, lock
from pydantic import BaseModel

from status import functioning as global_functioning, previous_functioning
from fastapi import Request



class NotificationPayload(BaseModel):
    title: str
    body: str

expo_push_tokens = set()

app = FastAPI()

event_loop = asyncio.get_event_loop()

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


VIDEO_DIR = "recordings"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # SHould be Replaced with app URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/internal-update-status")
async def update_status(request: Request):
    data = await request.json()
    new_status = data.get("functioning")

    global global_functioning, previous_functioning

    # if new_status != previous_functioning:
        # previous_functioning = new_status
        # global_functioning = new_status

    if not new_status:
        temp_token = "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
        send_push_notification(temp_token, "⛔ Stoppage Detected", "Production line has stopped!")
    else:
        temp_token = "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
        send_push_notification(temp_token, "✅ Production Running", "Production line is functioning normally!")

    return {"message": "Status updated"}


@app.get("/videos/{filename}")
def get_video(filename: str):
    file_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path=file_path, media_type='video/mp4')


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
        headers={
            "Content-Type": "application/json",
        },
    )
    print(f"📨 Sent notification to {token}: {response.status_code}")


@app.post("/send-notification")
async def send_notification(payload: NotificationPayload):
    # if not expo_push_tokens:
    #     return {"message": "No registered tokens"}

    # for token in expo_push_tokens:
    #     send_push_notification(token, payload.title, payload.body)

    # return {"message": f"Notification sent to {len(expo_push_tokens)} device(s)"}
    temp_token =  "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
    send_push_notification(temp_token, payload.title, payload.body)


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

    # if videos:
    #     for token in expo_push_tokens:
    #         send_push_notification(
    #             token,
    #             "📹 New Motion Detected!",
    #             f"{len(videos)} new video(s) available"
    #         )

    return {"new_videos": [os.path.basename(v) for v in videos]}

    
@app.get("/status")
def get_status():
    return {"status": "Running" if global_functioning else "Stopped"}
