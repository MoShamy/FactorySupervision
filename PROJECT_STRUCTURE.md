# Factory Supervision - Project Structure

## 📁 **Organized Directory Structure**

```
FactorySupervision/
├── 📂 frontend/                     # Frontend Dashboard & Server
│   ├── factory_dashboard.html       # Main web dashboard interface
│   └── dashboard_server.js          # Node.js server for frontend
│
├── 📂 backend/                      # Backend API Services
│   └── fastapi_server.py           # FastAPI server for backend services
│
├── 📂 computer_vision/              # Computer Vision & AI Processing
│   ├── conveyor_vision_system.py   # Main YOLO-based vision system
│   └── motion_detector.py          # Motion detection utilities
│
├── 📂 ai_chatbot/                   # AI Chatbot & Assistant
│   ├── factory_ai_assistant.py     # Main AI chatbot system
│   └── legacy_chatbot.py           # Previous chatbot implementation
│
├── 📂 config/                       # Configuration & Settings
│   └── system_status.py            # System status management
│
├── 📂 docs/                         # Documentation & Guides
│   ├── api_documentation.py        # Complete API documentation
│   └── security_setup.md           # Security configuration guide
│
├── 📂 Our_Models/                   # AI Models & Training
│   └── Best_Models/                # Trained YOLO models
│       └── bestdet.pt              # Best performing model
│
├── 📂 Dataset/                      # Training & Test Data
│   ├── Image/                      # Test images
│   └── Video/                      # Test videos
│
├── 📂 Results/                      # Output & Analysis
│   ├── Analysis_Reports/           # Generated reports
│   └── Processed_Videos/           # Processed video outputs
│
├── 📂 logs/                         # System Logs
│   └── production_status.log       # Production monitoring logs
│
├── 📂 .vscode/                      # Development Configuration
│   ├── launch.json                 # Debug configurations
│   └── tasks.json                  # Build tasks
│
├── 📂 tf-venv/                      # Python Virtual Environment
│
├── main.py                         # Main application entry point
├── package.json                    # Node.js dependencies
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (secret)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

## 🔗 **File Relationships & Dependencies**

### **Frontend Stack:**
- `frontend/factory_dashboard.html` → Web interface
- `frontend/dashboard_server.js` → Serves dashboard & handles chat

### **Backend Stack:**
- `backend/fastapi_server.py` → API server for system integration
- `computer_vision/conveyor_vision_system.py` → Core vision processing

### **AI Components:**
- `ai_chatbot/factory_ai_assistant.py` → Intelligent assistant
- `Our_Models/Best_Models/bestdet.pt` → YOLO detection model

### **Configuration:**
- `config/system_status.py` → Shared status management
- `.env` → Sensitive configuration data

## 🚀 **How to Run Each Component**

### **1. Start Vision System:**
```bash
python main.py
```

### **2. Start Backend API:**
```bash
# Using VS Code task
Ctrl+Shift+P → "Tasks: Run Task" → "start-backend"

# Or manually
cd backend
python -m uvicorn fastapi_server:app --reload --port 8001
```

### **3. Start Frontend Dashboard:**
```bash
# Using VS Code task
Ctrl+Shift+P → "Tasks: Run Task" → "start-frontend"

# Or manually
cd frontend
node dashboard_server.js
```

### **4. Test AI Chatbot:**
```bash
cd ai_chatbot
python factory_ai_assistant.py
```

## 🔧 **Development Workflow**

### **Debug Configurations Available:**
- **Debug C++ (main.cpp)** - For C++ development
- **Debug Python (main.py)** - Main application
- **Debug Python Vision System** - Computer vision debugging
- **Debug Python Chatbot** - AI assistant debugging  
- **Debug FastAPI Backend** - Backend API debugging

### **Build Tasks Available:**
- **build-cpp** - Compile C++ code
- **start-backend** - Launch FastAPI server
- **start-frontend** - Launch dashboard server
- **run-python-main** - Execute main application

## 📋 **File Name Changes Made**

| Old Name | New Name | Location |
|----------|----------|----------|
| `Dashboard.html` | `factory_dashboard.html` | `frontend/` |
| `server.js` | `dashboard_server.js` | `frontend/` |
| `backend.py` | `fastapi_server.py` | `backend/` |
| `YoloLineTest.py` | `conveyor_vision_system.py` | `computer_vision/` |
| `testting_chatbot.py` | `factory_ai_assistant.py` | `ai_chatbot/` |
| `detector.py` | `motion_detector.py` | `computer_vision/` |
| `status.py` | `system_status.py` | `config/` |
| `ConveyorVisionSystem_header.py` | `api_documentation.py` | `docs/` |
| `SECURITY_README.md` | `security_setup.md` | `docs/` |
| `simplified_chatgpt_data.py` | `legacy_chatbot.py` | `ai_chatbot/` |

## ✅ **Benefits of New Structure**

### **Organization:**
- **Clear separation** of frontend, backend, and AI components
- **Logical grouping** of related functionality
- **Easier navigation** and file discovery

### **Maintainability:**
- **Descriptive file names** that explain purpose
- **Consistent naming conventions**
- **Proper documentation** organization

### **Development:**
- **Easier debugging** with organized structure
- **Better collaboration** with clear responsibilities
- **Scalable architecture** for future growth

### **Deployment:**
- **Clear component boundaries** for containerization
- **Easier CI/CD** pipeline setup
- **Better error isolation**

This reorganized structure makes the project much more professional and maintainable! 🎉
