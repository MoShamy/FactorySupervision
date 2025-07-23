# 🏭 FactorySupervision - AI-Powered Production Line Monitoring

> **Comprehensive Documentation & Setup Guide**

FactorySupervision is a complete AI-powered system for monitoring production lines using computer vision, real-time analysis, and intelligent insights. This system provides a professional web dashboard with AI chat assistance for industrial factory supervision.

## 🎯 **System Overview**

### **Core Features**
- **🤖 Real-time Object Detection**: YOLO-based detection of production items (boxes, fruits, bags, bottles, jars, masks, pallets)
- **📊 Production Line Monitoring**: Virtual line detection with production flow analysis
- **🔍 Smart Status Detection**: Automatic identification of production states (running, slow, stopped)
- **💬 AI-Powered Chat**: Azure OpenAI integration for intelligent production insights
- **🎨 Modern Web Dashboard**: Professional interface with real-time monitoring
- **📹 Video Processing**: Automated processing and analysis of production footage
- **📋 Comprehensive Logging**: Detailed production logs with timestamps and analytics

### **System Architecture**
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

## 🚀 **Quick Start**

### **Prerequisites**
- **Python 3.10+** with virtual environment support
- **Node.js 16+** for frontend server
- **Azure OpenAI Account** for AI chat functionality
- **System Dependencies**:
  - **macOS**: `xcode-select --install`
  - **Linux**: `sudo apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1`
  - **Windows**: Visual C++ redistributable packages

### **Installation**

```bash
# 1. Clone repository
git clone <repository-url>
cd FactorySupervision

# 2. Set up Python environment
python -m venv tf-venv
source tf-venv/bin/activate  # macOS/Linux
# tf-venv\Scripts\activate    # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Node.js dependencies
npm install

# 5. Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### **Environment Configuration**
Create `.env` file with your Azure OpenAI credentials:
```env
AZURE_API_KEY=your_azure_openai_api_key
AZURE_ENDPOINT=https://your-resource.openai.azure.com
AZURE_DEPLOYMENT_NAME=your_deployment_name
AZURE_API_VERSION=2024-02-15-preview
```

### **Start the System**

**Option 1: Integrated Startup (Recommended)**
```bash
npm start
```

**Option 2: Manual Startup**
```bash
# Terminal 1: Backend
npm run start:backend

# Terminal 2: Frontend  
npm run start:frontend

# Terminal 3: Computer Vision (optional)
npm run vision
```

**Access the Dashboard:** `http://localhost:3000`

## 🏗️ **Project Structure**

```
FactorySupervision/
├── 📂 frontend/                     # Modern Web Dashboard
│   ├── index.html                   # Main dashboard entry point
│   ├── dashboard_server.js          # Node.js frontend server
│   ├── 📂 assets/                   # Static assets
│   │   ├── 📂 css/                  # Stylesheets
│   │   │   ├── main.css             # Core dashboard styles
│   │   │   └── chat.css             # Chat interface styles
│   │   └── 📂 js/                   # JavaScript modules
│   │       ├── main.js              # Application initialization
│   │       ├── chat.js              # AI chat system
│   │       ├── messageList.js       # Linked list implementation
│   │       └── navigation.js        # Page routing system
│   └── 📂 pages/                    # Individual page components
│       ├── dashboard.html           # Production overview
│       ├── cameras.html             # Camera monitoring
│       ├── alerts.html              # Alerts & notifications
│       ├── analytics.html           # Performance metrics
│       ├── files.html               # File management
│       └── settings.html            # System configuration
│
├── 📂 backend/                      # FastAPI Backend Services
│   ├── __init__.py
│   └── fastapi_server.py            # Main API server
│
├── 📂 computer_vision/              # AI Vision Processing
│   ├── __init__.py
│   ├── conveyor_vision_system.py    # YOLO-based detection system
│   └── motion_detector.py           # Motion detection utilities
│
├── 📂 ai_chatbot/                   # AI Assistant System
│   ├── __init__.py
│   ├── factory_ai_assistant.py      # Main AI chatbot
│   └── legacy_chatbot.py           # Previous implementation
│
├── 📂 config/                       # Configuration Management
│   ├── __init__.py
│   └── system_status.py             # System status management
│
├── 📂 docs/                         # Documentation
│   ├── api_documentation.py         # API reference
│   └── security_setup.md           # Security configuration
│
├── 📂 Our_Models/                   # AI Models & Training
│   ├── Best_Models/                # Production models
│   │   └── bestdet.pt              # Main YOLO model
│   ├── Model1_local/               # Local trained model
│   ├── Model1_collab/              # Collaborative model
│   ├── Model2/                     # Alternative model
│   └── Pre-trained_Models/         # Base YOLO models
│
├── 📂 Dataset/                      # Training & Test Data
│   ├── Image/                      # Test images for dashboard
│   └── Video/                      # Test videos for processing
│
├── 📂 Results/                      # Output & Analysis
│   ├── Analysis_Reports/           # Generated analysis reports
│   └── Processed_Videos/           # Computer vision output
│
├── 📂 logs/                         # System Logs
│   └── production_status.log       # Production monitoring logs
│
├── main.py                         # Application entry point
├── package.json                    # Node.js dependencies & scripts
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── .env.example                   # Environment template
└── README.md                      # This documentation
```

## 🎨 **Frontend Dashboard Features**

### **Modern Interface Design**
- **Professional Typography**: Inter font family for excellent readability
- **Glass-morphism Design**: Modern blur effects with gradient backgrounds
- **Responsive Layout**: Perfect on desktop, tablet, and mobile devices
- **Smooth Animations**: Subtle transitions and interactive feedback

### **Multi-Page Navigation**
- **📊 Dashboard**: Production overview with real-time metrics
- **📹 Camera Feeds**: Live monitoring from all production cameras  
- **🚨 Alerts & Reports**: System notifications and activity logs
- **📈 Analytics**: KPI dashboard with performance trends
- **🗂️ File Manager**: Access to logs, reports, and processed videos
- **⚙️ Settings**: System configuration and detection parameters

### **Enhanced AI Chat System**
- **Modern Messaging Interface**: WhatsApp/Telegram-inspired design
- **Intelligent Responses**: Azure OpenAI-powered production insights
- **Real-time Function Calls**: Direct integration with backend systems
- **Professional Context**: Factory and industrial terminology understanding
- **Error Handling**: User-friendly error messages and recovery

### **Chat Commands Examples**
```
"What's the current production status?"
"Show me computer vision analytics"
"Any recent alerts or system issues?"
"How many videos have been processed today?"
"Is the YOLO detection model working properly?"
"Show me today's efficiency metrics"
```

## 🤖 **AI & Computer Vision**

### **Object Detection Classes**
0. **Box** - Packaging containers
1. **Fruit** - Organic produce items  
2. **Bag** - Flexible packaging
3. **Bottle** - Liquid containers
4. **Jar** - Rigid containers
5. **Mask** - Safety equipment
6. **Pallet** - Transport platforms

### **Available Models**
- **Main Production**: `Our_Models/Best_Models/bestdet.pt`
- **Local Training**: `Our_Models/Model1_local/Model1_local.pt`
- **Collaborative**: `Our_Models/Model1_collab/model1.1.pt`
- **Alternative**: `Our_Models/Model2/model2.pt`

### **Configuration Parameters**
```python
line = False              # Line orientation (False=vertical, True=horizontal)
factor = 0.35            # Line position (35% of frame width/height)
cross_threshold = 4      # Seconds before considering stopped
targets = [0,1,2,3,4,5,6]  # Object classes to monitor
obj_per_time = 3         # Expected objects per time period
time_th = 10             # Time period in seconds
bounds = 1               # Tolerance margin
```

## 🌐 **API Endpoints**

### **Frontend Server (Port 3000)**
- `GET /` - Factory Dashboard
- `POST /chat` - AI Chat API with function calling
- `GET /health` - System health check with backend status

### **Backend Server (Port 8000)**
- `GET /status` - Current production status
- `GET /new-videos` - Recent motion detection results
- `POST /internal-update-status` - Production status updates
- `POST /send-notification` - Push notification system

### **AI Function Calls**
- `get_machine_status()` - Real-time production line status
- `get_activity_log()` - Production history and system logs
- `get_computer_vision_data()` - YOLO detection results and analytics

## 📊 **Usage Examples**

### **Basic Production Monitoring**
```bash
# Start complete system
npm start

# Run vision analysis only
python main.py

# Process specific video
python computer_vision/conveyor_vision_system.py [video_path]
```

### **Development Commands**
```bash
# Frontend development
cd frontend && node dashboard_server.js

# Backend development  
cd backend && python -m uvicorn fastapi_server:app --reload --port 8000

# AI chatbot testing
cd ai_chatbot && python factory_ai_assistant.py
```

## 🔧 **Advanced Configuration**

### **Tracker Setup** (Required for advanced tracking)
```bash
# Create tracker directory
mkdir -p ~/.config/ultralytics/trackers

# Add tracker configuration
cat > ~/.config/ultralytics/trackers/botsort.yaml << EOF
tracker_type: ocsort
appearance: True
match_thresh: 0.3
track_buffer: 100
proximity_thresh: 0.1
min_box_area: 10
vertical_ratio: 1.6
iou_thresh: 0
EOF
```

### **GPU Support** (Optional)
Uncomment GPU packages in `requirements.txt`:
```bash
# For CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🛠️ **Troubleshooting**

### **Common Issues & Solutions**

**Chat Not Working**
```bash
# Check Azure OpenAI credentials
cat .env

# Verify both servers running
curl http://localhost:3000/health
curl http://localhost:8000/status
```

**Model Not Found**
```bash
# Verify model files exist
ls -la Our_Models/Best_Models/bestdet.pt

# Check model path in code
grep -r "bestdet.pt" computer_vision/
```

**Video Processing Errors**
```bash
# Check video format (MP4, MOV, AVI supported)
file Dataset/Video/your_video.mp4

# Verify OpenCV installation
python -c "import cv2; print(cv2.__version__)"
```

**Dependencies Issues**
```bash
# Fresh virtual environment
rm -rf tf-venv
python -m venv tf-venv
source tf-venv/bin/activate
pip install -r requirements.txt

# Node.js dependencies
rm -rf node_modules package-lock.json
npm install
```

**Port Conflicts**
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8000

# Kill conflicting processes
sudo kill -9 <PID>
```

### **Debug Checklist**
- [ ] Python virtual environment activated (`tf-venv`)
- [ ] Python dependencies installed (`pip list | grep ultralytics`)
- [ ] Node.js dependencies installed (`npm list`)
- [ ] `.env` file exists with valid Azure OpenAI credentials
- [ ] Tracker configuration created (`~/.config/ultralytics/trackers/botsort.yaml`)
- [ ] Test images available (`ls Dataset/Image/`)
- [ ] YOLO model exists (`ls Our_Models/Best_Models/bestdet.pt`)

## 🚀 **Performance & Scaling**

### **System Requirements**
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8GB minimum, 16GB recommended for video processing
- **Storage**: 10GB+ free space for models and processed videos
- **GPU**: Optional but recommended for faster YOLO inference

### **Optimization Tips**
- Use GPU acceleration for faster computer vision processing
- Adjust YOLO confidence thresholds based on your specific use case
- Implement video streaming instead of file processing for real-time applications
- Use load balancing for multiple production lines

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for Industrial Factory Supervision and AI-Powered Production Monitoring** 🏭✨

For questions, issues, or feature requests, please open an issue on the repository.
