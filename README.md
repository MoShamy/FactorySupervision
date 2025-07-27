# 🏭 Factory Supervision Dashboard

A comprehensive factory monitoring and supervision system with real-time computer vision, AI-powered analytics, and an intuitive web-based dashboard.

## ✨ Features

- **🎯 Real-time Computer Vision**: YOLO-based object detection and motion tracking
- **📊 Interactive Dashboard**: Modern web interface with glass-morphism design
- **🤖 AI Assistant**: Intelligent chatbot for factory insights and troubleshooting
- **📈 Analytics & Reports**: Production metrics, efficiency tracking, and alerts
- **📹 Multi-Camera Support**: Live camera feeds with processing capabilities
- **🔄 Real-time Updates**: Live status monitoring and notifications

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MoShamy/FactorySupervision.git
   cd FactorySupervision
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Running the Application

#### Option 1: Quick Start (Recommended)
```bash
./start_system.sh
```

#### Option 2: Manual Start

1. **Start Frontend Server**
   ```bash
   cd frontend
   node server.js
   ```

2. **Start Backend API** (Optional - for full features)
   ```bash
   cd backend
   python -m uvicorn fastapi_server:app --reload --port 8000
   ```

3. **Access Dashboard**
   - Open browser: http://localhost:3000

## 📁 Project Structure

```
FactorySupervision/
├── 📂 frontend/          # Web Dashboard & Server
│   ├── index.html        # Main dashboard interface
│   ├── server.js         # Simple Express server
│   ├── dashboard_server.js # Full-featured server
│   ├── assets/           # CSS, JS, and images
│   └── pages/            # Dashboard page components
│
├── 📂 backend/           # API Services
│   └── fastapi_server.py # FastAPI backend server
│
├── 📂 computer_vision/   # Computer Vision & AI
│   └── conveyor_vision_system.py # YOLO-based vision
│
├── 📂 Our_Models/        # AI Models
│   └── Best_Models/      # Trained YOLO models
│
├── 📂 Dataset/           # Training & Test Data
│   ├── Image/            # Test images
│   └── Video/            # Test videos
│
└── 📂 Results/           # Output & Analysis
    ├── Analysis_Reports/ # Generated reports
    └── Processed_Videos/ # Processed outputs
```

## 🎨 Dashboard Features

### Design System
- **Glass-morphism UI**: Modern translucent design with depth
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Smooth hover effects and animations
- **Professional Typography**: Multi-font system for clarity

### Core Sections
- **📊 Dashboard**: System overview and key metrics
- **📹 Camera Feeds**: Live video monitoring with controls
- **🚨 Alerts & Reports**: Real-time notifications and analysis
- **📈 Analytics**: Performance metrics and trends
- **📁 Files**: Data management and downloads
- **⚙️ Settings**: System configuration

### Chat Assistant
- **🤖 AI-Powered**: Intelligent responses about factory operations
- **📱 Resizable**: Compact corner chat or full conversation mode
- **💬 Real-time**: Instant responses and status updates

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Azure OpenAI (Optional - for full AI features)
AZURE_API_KEY=your_azure_api_key
AZURE_ENDPOINT=your_azure_endpoint
AZURE_DEPLOYMENT_NAME=your_model_name
AZURE_API_VERSION=2023-12-01-preview

# Server Configuration
PORT=3000
NODE_ENV=development
```

## 🛠️ Development

### VS Code Setup
The project includes VS Code configurations for debugging and tasks:

- **Debug Configurations**: Python, Node.js, and FastAPI debugging
- **Build Tasks**: Automated start commands for all services
- **Extensions**: Recommended extensions for development

### Available Scripts

```bash
# Frontend development
npm run dev          # Start frontend with hot reload
npm start           # Start production frontend

# Python services
python main.py      # Start computer vision system
```

## 📊 API Endpoints

### Frontend Server (Port 3000)
- `GET /` - Main dashboard
- `POST /api/chat` - Chat assistant
- `GET /health` - Server health check
- `GET /pages/:page` - Dynamic page loading

### Backend Server (Port 8000) - Optional
- `GET /status` - System status
- `GET /health` - Backend health
- `POST /chat` - Full AI chat with function calling

## 🔒 Security

- Environment variables for sensitive data
- CORS protection for API endpoints
- Input validation and sanitization
- Secure file handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mostafa** - [MoShamy](https://github.com/MoShamy)

## 🙏 Acknowledgments

- YOLO models for computer vision
- Express.js for web framework
- Azure OpenAI for AI capabilities
- Glass-morphism design inspiration

---

**🏭 Factory Supervision Dashboard** - Modern factory monitoring made simple.
