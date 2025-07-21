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
   ```bash
   python -m venv tf-venv
   source tf-venv/bin/activate  # On Windows: tf-venv\Scripts\activate
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
   ```bash
   mkdir -p ~/.config/ultralytics/trackers
   nano ~/.config/ultralytics/trackers/botsort.yaml
   ```
   
   Add the following content to `botsort.yaml`:
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

## 📁 Project Structure

```
FactorySupervision/
├── main.py                     # Main entry point
├── YoloLineTest.py            # Core production monitoring logic
├── simplified_chatgpt_data.py # AI analysis module
├── requirements.txt           # Project dependencies
├── Dataset/                   # Input data
│   ├── Video/                # Test videos
│   └── Image/                # Test images
├── Our_Models/               # Trained models
│   ├── Model1_local/         # Local trained model
│   ├── Model1_collab/        # Collaborative model
│   ├── Model2/               # Main production model
│   └── Pre-trained_Models/   # YOLOv8 base models
├── Results/                  # Output directory
│   ├── Processed_Videos/     # Annotated videos
│   └── Analysis_Reports/     # AI analysis reports
├── logs/                     # Production logs
└── tf-venv/                  # Virtual environment
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

### Training New Models
Use the Jupyter notebooks in `Our_Models/` for model training:
- `Model_Training.ipynb` - Train new models
- `Model_Testing_Comprehensive.ipynb` - Test model performance

### Adding New Features
- Modify `YoloLineTest.py` for core detection logic
- Update `simplified_chatgpt_data.py` for AI analysis features
- Use `main.py` as the integration point

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

5. **Dependency installation issues**
   - **OpenCV errors**: Install system dependencies (see Prerequisites)
   - **GPU issues**: Uncomment torch packages in requirements.txt for CUDA support
   - **Permission errors**: Use `pip install --user` or check virtual environment activation
   - **Version conflicts**: Create fresh virtual environment and reinstall

6. **Jupyter notebook issues**
   - Install kernel: `python -m ipykernel install --user --name=tf-venv`
   - Select correct kernel in Jupyter: Kernel > Change Kernel > tf-venv


## 📄 License

[Add your license information here]
