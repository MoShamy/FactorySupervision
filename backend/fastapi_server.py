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
from typing import Optional
# from notifications import send_push_notification, expo_push_tokens
import requests
import sys

# Add project directories to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'computer_vision'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))

from computer_vision.motion_detector import CameraMotionDetector, recorded_videos_queue, lock
from pydantic import BaseModel

import config.system_status as status
from fastapi import Request

# Import AI Chatbot Service
try:
    from ai_chatbot_service import chatbot_service
    CHATBOT_ENABLED = True
except ImportError:
    CHATBOT_ENABLED = False
    print("AI Chatbot service not available - continuing without chatbot features")



class NotificationPayload(BaseModel):
    title: str
    body: str

expo_push_tokens = set()

app = FastAPI()

event_loop = asyncio.get_event_loop()

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

VIDEO_DIR = "recordings"

# Initialize AI Chatbot on startup
@app.on_event("startup")
async def startup_event():
    if CHATBOT_ENABLED:
        try:
            await chatbot_service.initialize()
            print("✅ AI Chatbot Service initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize AI Chatbot Service: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    if CHATBOT_ENABLED:
        try:
            chatbot_service.stop()
            print("✅ AI Chatbot Service stopped")
        except Exception as e:
            print(f"❌ Error stopping AI Chatbot Service: {e}")

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
    print("🔄 Updating status from internal request")

    # global global_functioning, previous_functioning

    # if new_status != previous_functioning:
        # previous_functioning = new_status
    # status.functioning = new_status
    # print(f"global functioning = {status.functioning}")

    temp_token = "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
    if new_status:
        send_push_notification(temp_token, "✅ Production Running", "Production line is functioning normally!")
    else:
        send_push_notification(temp_token, "⛔ Stoppage Detected", "Production line has stopped!")
        temp_token = "ExponentPushToken[DtaKDBNEHe0CJyforTbFH9]"
       

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
    # Get enhanced status information
    status_info = status.get_status()
    return {
        "status": status_info['status_text'],
        "functioning": status_info['functioning'],
        "last_change": status_info['last_change'],
        "uptime": status_info['uptime'],
        "recent_history": status_info['recent_history']
    }

@app.post("/refresh-status")
def refresh_status():
    """Force refresh status from log files"""
    status.refresh_status()
    return {"message": "Status refreshed from logs", "status": status.get_status()}

# AI Chatbot endpoints
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

@app.post("/chat")
async def chat_with_ai(chat_request: ChatMessage):
    """Chat with AI assistant that has context of production logs"""
    if not CHATBOT_ENABLED:
        raise HTTPException(status_code=503, detail="AI Chatbot service not available")
    
    try:
        response = await chatbot_service.chat(
            chat_request.message, 
            chat_request.conversation_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/chat/status")
async def get_chatbot_status():
    """Get AI chatbot service status and memory info"""
    if not CHATBOT_ENABLED:
        return {"enabled": False, "status": "disabled"}
    
    try:
        log_memory_count = sum(len(entries) for entries in chatbot_service.log_memory.values())
        return {
            "enabled": True,
            "status": "active",
            "log_files_monitored": len(chatbot_service.log_memory),
            "total_log_entries": log_memory_count,
            "conversation_history_length": len(chatbot_service.conversation_history),
            "last_context_update": getattr(chatbot_service, 'last_update', None)
        }
    except Exception as e:
        return {"enabled": True, "status": "error", "error": str(e)}
