
# 🏭 FactorySupervision - AI-Powered Production Line Monitoring

FactorySupervision is an AI-powered system for monitoring production lines using computer vision. It detects objects, tracks their movement across virtual lines, and provides real-time analysis of production status with AI-powered insights.

## 🎯 Features

- **Real-time Object Detection**: Uses YOLOv8 models to detect production items (boxes, fruits, bags, bottles, jars, masks, pallets)
- **Production Line Monitoring**: Virtual line detection to count objects and monitor production flow
- **Status Detection**: Identifies if production is running, slow, or stopped
- **AI Analysis**: ChatGPT integration for production data analysis and insights
- **Video Processing**: Processes input videos and generates annotated output videos
- **Logging**: Comprehensive production logging with timestamps

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)
- **System Dependencies**:
  - **macOS**: Xcode command line tools (`xcode-select --install`)
  - **Linux**: `sudo apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1`
  - **Windows**: Visual C++ redistributable packages

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd FactorySupervision
```

2. **Set up virtual environment**

For macOS/Linux:
```bash
python -m venv tf-venv
source tf-venv/bin/activate
```

For Windows:
```bash
python -m venv tf-venv
tf-venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```
   
   **Alternative: Manual installation of core dependencies**

```bash
pip install ultralytics opencv-python numpy supervision openai
pip install jupyter ipykernel  # For notebook support
```

   **Note**: For detailed dependency information, see `requirements.txt` which includes:
   - **Core ML/CV**: ultralytics, opencv-python, numpy, supervision
   - **AI Analysis**: openai (for ChatGPT integration)
   - **Development**: jupyter, ipykernel, matplotlib
   - **Optional**: GPU support packages (see comments in requirements.txt)

4. **Set up object tracking (Required for advanced tracking)**

For macOS/Linux:
```bash
mkdir -p /.config/ultralytics/trackers
```

For Windows:
```bash
mkdir "\.config\ultralytics\trackers"

```

   Add the following content to `\.config\ultralytics\trackers\botsort.yaml`:
   ```yaml
   tracker_type: ocsort
   appearance: True
   match_thresh: 0.3
   track_buffer: 100
   proximity_thresh: 0.1
   min_box_area: 10
   vertical_ratio: 1.6
   iou_thresh: 0
   ```

### Running the System

1. **Basic Usage**

```bash
python main.py
```

   This will process the default test video and generate analysis.

2. **Analyze specific video**

```bash
python YoloLineTest.py [video_path]
```

3. **Run AI analysis only**

```bash
python simplified_chatgpt_data.py
```

4. **Run Web Dashboard (with AI Chat)**

```bash
# Install Node.js dependencies
npm install

# Start the web server
npm start
# OR
node server.js
```
   
   The dashboard will be available at `http://localhost:3000` and includes:
   - Real-time production monitoring display
   - AI-powered chat assistant for production insights
   - Visual feed displays using your dataset images

## 🌐 Web Dashboard Setup

The project includes a web-based dashboard (`Dashboard.html`) with an AI chat interface powered by Azure OpenAI.

### Server Configuration

1. **Install Node.js dependencies**

```bash
npm install
```

2. **Environment Setup**
   Create a `.env` file in the root directory with your Azure OpenAI credentials: (follow the guide: `.env.example`) 
   ```env
   AZURE_API_KEY=your_azure_openai_api_key
   AZURE_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_DEPLOYMENT_NAME=your_deployment_name
   AZURE_API_VERSION=2024-02-15-preview
   ```

3. **Start the server**

```bash
npm start
```

   The server will run on port 3000 by default.

### Dashboard Features
- **Production Monitoring**: Visual displays using images from `Dataset/Image/`
- **AI Chat Assistant**: Real-time chat with production data analysis
- **Responsive Design**: Futuristic CCTV-style interface
- **Real-time Updates**: Integration with production monitoring system

### Important Notes
- The `.env` file is gitignored for security
- Server uses Express.js with CORS enabled for frontend integration
- Azure OpenAI integration provides intelligent production insights
- Dashboard displays actual images from your dataset instead of placeholders

## 📁 Project Structure

```
FactorySupervision/
├── main.py                     # Main entry point
├── YoloLineTest.py            # Core production monitoring logic
├── simplified_chatgpt_data.py # AI analysis module
├── server.js                  # Express.js web server
├── Dashboard.html             # Web dashboard interface
├── package.json               # Node.js dependencies
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .gitignore                 # Git ignore file
├── Dataset/                   # Input data
│   ├── Video/                # Test videos
│   └── Image/                # Test images (used in dashboard)
├── Our_Models/               # Trained models
│   ├── Model1_local/         # Local trained model
│   ├── Model1_collab/        # Collaborative model
│   ├── Model2/               # Main production model
│   └── Pre-trained_Models/   # YOLOv8 base models
├── Results/                  # Output directory
│   ├── Processed_Videos/     # Annotated videos
│   └── Analysis_Reports/     # AI analysis reports
├── logs/                     # Production logs
├── node_modules/             # Node.js packages (auto-generated)
└── tf-venv/                  # Python virtual environment
```

## 🤖 Available Models

### Production Models
- **Model2** (`Our_Models/Model2/model2.pt`) - Main production model (currently used)
- **Model1_local** (`Our_Models/Model1_local/Model1_local.pt`) - Local trained model
- **Model1_collab** (`Our_Models/Model1_collab/model1.1.pt`) - Collaborative model

### Pre-trained Models
- YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l - Base YOLO models

### Object Classes Detected
0. Box
1. Fruit  
2. Bag
3. Bottle
4. Jar
5. Mask
6. Pallet

## ⚙️ Configuration Parameters

Key parameters for production monitoring (in `main.py`):

```python
line = False              # False=vertical line, True=horizontal line
factor = 0.35            # Line position (35% of frame width/height)
cross_threshold = 4      # Seconds before considering stopped
targets = [0,1,2,3,4,5,6]  # Object classes to monitor
obj_per_time = 3         # Expected objects per time period
time_th = 10             # Time period in seconds
bounds = 1               # Tolerance margin
```

## 📊 Output

The system generates:
- **Processed Videos**: Annotated videos with bounding boxes and status
- **Production Logs**: Timestamped production status logs
- **AI Analysis**: ChatGPT-powered insights and recommendations

## 🔧 Development

### Environment Variables and Security

The project uses environment variables for sensitive configuration:

1. **Required Environment Variables** (create `.env` file):
   ```env
   AZURE_API_KEY=your_azure_openai_api_key
   AZURE_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_DEPLOYMENT_NAME=your_deployment_name
   AZURE_API_VERSION=2024-02-15-preview
   ```

2. **Git Ignore Configuration**
   The `.gitignore` file excludes:
   - `tf-venv/` - Python virtual environment
   - `.env` - Environment variables (security)
   - `node_modules/` - Node.js packages
   - `*.mp4`, `*.mov` - Video files (large files)
   - `__pycache__/`, `*.pyc` - Python cache files
   - `.DS_Store` - macOS system files
   - `*.png` - Image files
   - `frontend_ref/` - Frontend reference materials

### Training New Models
Use the Jupyter notebooks in `Our_Models/` for model training:
- `Model_Training.ipynb` - Train new models
- `Model_Testing_Comprehensive.ipynb` - Test model performance

### Adding New Features
- Modify `YoloLineTest.py` for core detection logic
- Update `simplified_chatgpt_data.py` for AI analysis features
- Use `main.py` as the integration point
- Update `server.js` for web API endpoints
- Modify `Dashboard.html` for frontend changes

## 🐛 Troubleshooting

### Common Issues

1. **Model not found error**
   - Ensure model files exist in `Our_Models/` directory
   - Check file paths in the code

2. **Video processing errors**
   - Verify video file format (MP4, MOV, AVI supported)
   - Check video file isn't corrupted

3. **Tracking issues**
   - Ensure `botsort.yaml` is properly configured
   - Check ultralytics installation

4. **Environment issues**
   - Activate virtual environment: `source tf-venv/bin/activate`
   - Install missing dependencies: `pip install -r requirements.txt`

5. **Web Server Issues**
   - **Port already in use**: Change port in `server.js` or stop conflicting process
   - **Missing .env file**: Create `.env` with required Azure OpenAI credentials
   - **Node.js dependencies**: Run `npm install` to install required packages
   - **CORS errors**: Server has CORS enabled, check network configuration
   - **Azure OpenAI errors**: Verify API key, endpoint, and deployment name in `.env`

6. **Dashboard Issues**
   - **Images not loading**: Check that `Dataset/Image/` contains test images
   - **Chat not working**: Verify server is running and `.env` is configured
   - **Styling issues**: Ensure all CSS files are properly linked

7. **Dependency installation issues**
   - **OpenCV errors**: Install system dependencies (see Prerequisites)
   - **GPU issues**: Uncomment torch packages in requirements.txt for CUDA support
   - **Permission errors**: Use `pip install --user` or check virtual environment activation
   - **Version conflicts**: Create fresh virtual environment and reinstall

8. **Jupyter notebook issues**
   - Install kernel: `python -m ipykernel install --user --name=tf-venv`
   - Select correct kernel in Jupyter: Kernel > Change Kernel > tf-venv

### Environment Setup Checklist

- [ ] Python virtual environment activated (`tf-venv`)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Node.js dependencies installed (`npm install`)
- [ ] `.env` file created with Azure OpenAI credentials
- [ ] Tracker configuration file created (`~/.config/ultralytics/trackers/botsort.yaml`)
- [ ] Test images available in `Dataset/Image/`


## 📄 License

[Add your license information here]
