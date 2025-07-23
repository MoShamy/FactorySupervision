# Factory Supervision System - Full Integration Guide

## 🏭 System Architecture

The Factory Supervision System now uses a **complete integration** between frontend, backend, and computer vision components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Frontend      │    │   FastAPI        │    │  Computer Vision    │
│   Dashboard     │◄──►│   Backend        │◄──►│   System            │
│   (Port 3000)   │    │   (Port 8000)    │    │   (YOLO + OpenCV)   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Azure OpenAI  │    │  Motion Detection│    │   Production Logs   │
│   Chat API      │    │  Push Notifications  │    │   Status Files      │
│   (gpt-35-turbo)│    │  Video Management│    │   Result Analysis   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## 🚀 Quick Start

### Option 1: Integrated Startup (Recommended)
```bash
# Start everything at once
npm start
# or
./start_system.sh
```

### Option 2: Manual Startup
```bash
# Terminal 1: Start FastAPI Backend
npm run start:backend

# Terminal 2: Start Frontend
npm run start:frontend
```

## 🔧 Component Details

### 📡 **Frontend Server** (`frontend/dashboard_server.js`)
- **Port**: 3000
- **Features**:
  - Real-time AI chat with Azure OpenAI
  - Integrated API calls to FastAPI backend
  - Computer vision data visualization
  - Production status monitoring
  - Error handling and fallback systems

### ⚙️ **FastAPI Backend** (`backend/fastapi_server.py`)
- **Port**: 8000
- **Features**:
  - Motion detection and camera monitoring
  - Production status tracking
  - Push notifications for mobile devices
  - Video recording and management
  - Direct integration with computer vision system

### 🤖 **AI Chat Integration**
- **Model**: Azure OpenAI gpt-35-turbo
- **Functions Available**:
  - `get_machine_status()` - Real-time production line status
  - `get_activity_log()` - Production history and logs
  - `get_computer_vision_data()` - YOLO detection results and analytics

### 👁️ **Computer Vision System**
- **Model**: YOLO Best Detection (`Our_Models/Best_Models/bestdet.pt`)
- **Features**:
  - Real-time object detection
  - Conveyor belt monitoring
  - Production line analysis
  - Automated status updates

## 🌐 API Endpoints

### Frontend (Port 3000)
- `GET /` - Factory Dashboard
- `POST /chat` - AI Chat API
- `GET /health` - System Health Check

### Backend (Port 8000)
- `GET /status` - Production Status
- `GET /new-videos` - Recent Motion Detections
- `POST /internal-update-status` - Status Updates
- `POST /send-notification` - Push Notifications

## 💬 Chat Commands

Try these commands in the dashboard chat:

```
"What's the current machine status?"
"Show me computer vision data"
"Any recent production issues?"
"How many videos have been processed?"
"What's in the activity log?"
"Is the YOLO model working?"
```

## 🔍 Data Flow

1. **Computer Vision** processes video feeds and updates status
2. **FastAPI Backend** receives status updates and stores data
3. **Frontend Chat** queries backend via API calls
4. **Azure OpenAI** processes queries and calls appropriate functions
5. **Real-time responses** displayed in dashboard chat

## 🛠️ Configuration Files

- `.env` - Azure OpenAI credentials and API settings
- `config/system_status.py` - Production line status
- `logs/production_status.log` - Activity logging
- `package.json` - NPM scripts and dependencies

## 📊 Monitoring

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:3000/health
- **Logs**: Check terminal output for real-time monitoring

## 🔧 Troubleshooting

### Chat Not Working
1. Check Azure OpenAI credentials in `.env`
2. Verify both servers are running
3. Test health endpoint: `curl http://localhost:3000/health`

### Backend Connection Issues
1. Ensure FastAPI is running on port 8000
2. Check for port conflicts
3. Verify Python dependencies are installed

### Computer Vision Data Missing
1. Run the vision system: `npm run vision`
2. Check `Results/` directory for processed data
3. Verify YOLO model exists in `Our_Models/Best_Models/`

## 🎯 Success Indicators

✅ Both servers start without errors  
✅ Health check shows FastAPI backend connected  
✅ Chat responds with AI-generated answers  
✅ Function calls retrieve real production data  
✅ Computer vision data includes processed videos  
✅ Machine status reflects actual system state  

---

**The system is now fully integrated with real-time computer vision, production monitoring, and AI-powered insights!** 🎉
