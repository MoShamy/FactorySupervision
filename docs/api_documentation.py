"""
==============================================================================
CONVEYOR VISION SYSTEM - COMPUTER VISION MODULE
==============================================================================

Author: Factory Supervision Team
Date: July 22, 2025
Version: 2.0.0
License: MIT

Description:
    Advanced computer vision system for real-time conveyor belt monitoring
    and object detection using YOLO deep learning models. Provides automated
    status monitoring, anomaly detection, and production line analytics.

Dependencies:
    - OpenCV (cv2)
    - Ultralytics YOLO
    - NumPy
    - Requests
    - Python 3.8+

==============================================================================
MODULE OVERVIEW
==============================================================================

Main Classes:
    - DetectedObject: Data class for object tracking
    - ConveyorVisionSystem: Main computer vision processing system

Key Features:
    ✅ Real-time object detection and tracking
    ✅ Virtual line crossing detection
    ✅ Production status monitoring
    ✅ Anomaly detection and logging
    ✅ Backend integration via REST API
    ✅ Video processing and output
    ✅ Statistical analysis and reporting

==============================================================================
CLASS: ConveyorVisionSystem
==============================================================================

Purpose:
    Comprehensive computer vision system for monitoring conveyor belt 
    operations, detecting objects, tracking their movement, and analyzing
    production efficiency in real-time.

Core Methods:

    INITIALIZATION & SETUP:
    ├── __init__(model_path)                    - Initialize system with YOLO model
    ├── initialize_video_capture(...)           - Set up video input/output
    ├── setup_virtual_line(...)                 - Configure detection line
    └── configure_detection_parameters(...)     - Set monitoring parameters

    VISION PROCESSING:
    ├── detect_objects(frame)                   - Perform YOLO object detection
    ├── process_detected_object(...)            - Handle individual detections
    ├── _process_target_object(...)             - Process target class objects
    └── _process_anomaly_object(...)            - Handle anomaly detection

    LINE CROSSING DETECTION:
    ├── _check_line_crossing(...)               - Detect line crossings
    └── _update_object_position(...)            - Track object positions

    STATUS MONITORING:
    ├── analyze_system_status()                 - Determine system health
    ├── _notify_status_change(...)              - Communicate with backend
    └── _log_status(...)                        - Log status changes

    VISUALIZATION & OUTPUT:
    ├── draw_virtual_line(...)                  - Draw detection line
    ├── add_frame_overlay(...)                  - Add overlays to video
    └── get_crossing_statistics()               - Calculate metrics

    RESOURCE MANAGEMENT:
    ├── cleanup()                               - Release video resources
    └── run_monitoring(...)                     - Main execution method

==============================================================================
USAGE EXAMPLES
==============================================================================

Basic Usage:
    ```python
    # Initialize the vision system
    vision_system = ConveyorVisionSystem("path/to/model.pt")
    
    # Run complete monitoring
    vision_system.run_monitoring(
        video_path="input_video.mp4",
        output_log_path="logs/production.log",
        line_factor=0.5,
        is_horizontal_line=True,
        cross_threshold=0.5,
        targets=[0, 1, 2],  # Object class IDs
        obj_per_time=10,
        time_threshold=60,
        bounds=2
    )
    ```

Advanced Usage:
    ```python
    # Step-by-step configuration
    vision_system = ConveyorVisionSystem()
    
    # Configure parameters
    vision_system.configure_detection_parameters(
        targets=[0, 1, 2],
        obj_per_time=10,
        time_threshold=60,
        bounds=2,
        output_log_path="logs/production.log"
    )
    
    # Set up video processing
    width, height, fps = vision_system.initialize_video_capture("input.mp4")
    vision_system.setup_virtual_line(width, height, 0.5, True)
    
    # Process individual frames
    while vision_system.cap.isOpened():
        ret, frame = vision_system.cap.read()
        if not ret:
            break
            
        results = vision_system.detect_objects(frame)
        # ... process results
        
    vision_system.cleanup()
    ```

Legacy Compatibility:
    ```python
    # Use original function interface
    OperationStatus(
        video_path="input.mp4",
        out_path="logs/production.log",
        line=True,              # horizontal line
        factor=0.5,
        cross_threshold=0.5,
        targets=[0, 1, 2],
        obj_per_time=10,
        time_th=60,
        bounds=2
    )
    ```

==============================================================================
CONFIGURATION PARAMETERS
==============================================================================

Video Processing:
    - video_path: Input video file path
    - output_video_path: Processed video output path
    - line_factor: Position of virtual line (0.0-1.0)
    - is_horizontal_line: True for horizontal, False for vertical

Detection Settings:
    - model_path: Path to YOLO model file
    - targets: List of target object class IDs
    - cross_threshold: Minimum time between crossings (seconds)

Status Monitoring:
    - obj_per_time: Expected objects per time window
    - time_threshold: Time window for analysis (seconds)
    - bounds: Tolerance range for normal operation
    - output_log_path: Path for status log file

Backend Integration:
    - Backend URL: http://localhost:8001/internal-update-status
    - Status updates sent automatically on changes

==============================================================================
SYSTEM STATUS STATES
==============================================================================

NORMAL OPERATION:
    ✅ Object count within expected range (obj_per_time ± bounds)
    ✅ Regular object crossings detected
    ✅ No anomalies detected

ERROR STATES:
    ⚠️  TOO FAST: Object count > (obj_per_time + bounds)
    ⚠️  TOO SLOW: Object count < (obj_per_time - bounds) and > 0
    ❌ STOPPED: No objects detected in time window
    🔍 ANOMALY: Non-target objects detected on line

==============================================================================
OUTPUT FILES
==============================================================================

Log File Format:
    - Status changes with timestamps
    - Anomaly detections
    - System start/stop events
    
Video Output:
    - Processed video with bounding boxes
    - Virtual line overlay
    - Object count display
    - Object ID tracking

Statistics:
    - Standard deviation of crossing times
    - Mean crossing time
    - Total crossings count

==============================================================================
ERROR HANDLING
==============================================================================

Common Issues:
    - Model file not found: Check model_path parameter
    - Video file not accessible: Verify video_path exists
    - Backend connection failed: Check server status
    - OpenCV display issues: Ensure GUI support available

Troubleshooting:
    - Enable verbose logging for detailed output
    - Check system resources (CPU, memory, GPU)
    - Verify YOLO model compatibility
    - Ensure proper video codec support

==============================================================================
PERFORMANCE OPTIMIZATION
==============================================================================

Recommendations:
    ⚡ Use GPU acceleration for YOLO inference
    ⚡ Optimize video resolution for processing speed
    ⚡ Adjust confidence thresholds for accuracy vs speed
    ⚡ Use appropriate tracker settings (botsort.yaml)
    ⚡ Monitor memory usage for long-running processes

Hardware Requirements:
    - CPU: Multi-core processor recommended
    - RAM: 8GB minimum, 16GB recommended
    - GPU: CUDA-compatible GPU for acceleration
    - Storage: SSD for video processing

==============================================================================
API INTEGRATION
==============================================================================

Backend Endpoints:
    POST /internal-update-status
    Request: {"functioning": boolean}
    Response: {"updated": boolean, "functioning": boolean}

Status Monitoring:
    - Automatic status updates on changes
    - Real-time system health monitoring
    - Integration with factory management systems

==============================================================================
CHANGELOG
==============================================================================

Version 2.0.0 (Current):
    + Complete object-oriented refactor
    + Improved error handling and logging
    + Enhanced statistics and reporting
    + Better resource management
    + Comprehensive documentation

Version 1.0.0 (Legacy):
    + Basic functionality with single function
    + YOLO object detection
    + Line crossing detection
    + Status monitoring

==============================================================================
"""
