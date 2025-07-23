"""
==============================================================================
CONVEYOR VISION SYSTEM - MAIN MODULE
==============================================================================
File: conveyor_vision_system.py
Author: Factory Supervision Team
Date: July 22, 2025
Version: 2.0.0

Description:
    Advanced computer vision system for real-time conveyor belt monitoring
    using YOLO object detection. Provides automated production line monitoring,
    object tracking, anomaly detection, and system status analysis.

Main Classes:
    - DetectedObject: Data structure for tracked objects
    - ConveyorVisionSystem: Complete vision processing system

Usage:
    # Object-oriented approach
    vision_system = ConveyorVisionSystem("model.pt")
    vision_system.run_monitoring(...)
    
    # Legacy function approach
    OperationStatus(video_path, out_path, ...)

Dependencies:
    - cv2 (OpenCV)
    - ultralytics (YOLO)
    - numpy
    - requests
    - system_status module

For detailed documentation, see: docs/api_documentation.py
==============================================================================
"""

import cv2
import time
from ultralytics import YOLO
import json
import numpy as np
from dataclasses import dataclass
import sys
import os

# Add config directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
import system_status as status
import requests

@dataclass
class DetectedObject:
    centerx: float
    centery: float
    detect: bool

class ConveyorVisionSystem:
    """Computer Vision System for Conveyor Belt Monitoring"""
    
    def __init__(self, model_path="Our_Models/Best_Models/bestdet.pt"):
        """Initialize the vision system with YOLO model"""
        self.model = YOLO(model_path)
        self.previous_positions = {}
        self.anomaly_objects = {}
        self.time_between_crossings = []
        self.obj_count = 0
        self.frame_count = 0
        self.last_cross_time = time.time()
        self.start_time = time.time()
        
        # Video processing objects
        self.cap = None
        self.out_video = None
        
        # Configuration parameters
        self.line_x = 0
        self.line_y = 0
        self.is_horizontal_line = True
        self.cross_threshold = 0.5
        self.targets = []
        self.obj_per_time = 0
        self.time_threshold = 0
        self.bounds = 0
        self.output_log_path = ""
    
    def initialize_video_capture(self, video_path, output_video_path="output_processed.mp4"):
        """Initialize video capture and output writer"""
        self.cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        # Initialize VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        return width, height, fps
    
    def setup_virtual_line(self, width, height, factor, is_horizontal=True):
        """Set up the virtual line for object crossing detection"""
        self.is_horizontal_line = is_horizontal
        if is_horizontal:
            self.line_y = int(height * factor)
            self.line_x = 0  # Not used for horizontal line
        else:
            self.line_x = int(width * factor)
            self.line_y = 0  # Not used for vertical line
    
    def configure_detection_parameters(self, targets, obj_per_time, time_threshold, bounds, output_log_path):
        """Configure detection and monitoring parameters"""
        self.targets = targets
        self.obj_per_time = obj_per_time
        self.time_threshold = time_threshold
        self.bounds = bounds
        self.output_log_path = output_log_path
    
    def draw_virtual_line(self, frame, width, height):
        """Draw the virtual line on the frame"""
        if self.is_horizontal_line:
            cv2.line(frame, (0, self.line_y), (width, self.line_y), (0, 0, 255), 2)
        else:
            cv2.line(frame, (self.line_x, 0), (self.line_x, height), (0, 0, 255), 2)
    
    def detect_objects(self, frame):
        """Perform object detection on the frame"""
        results = self.model.track(
            source=frame, 
            conf=0.1, 
            iou=0.5, 
            show=False, 
            persist=True, 
            tracker="botsort.yaml", 
            verbose=False
        )
        return results
    
    def process_detected_object(self, box, obj_id, obj_class, frame):
        """Process a single detected object"""
        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        
        current_obj = DetectedObject(cx, cy, False)
        
        if obj_class in self.targets:
            self._process_target_object(current_obj, obj_id, x1, y1, x2, y2, frame)
        else:
            self._process_anomaly_object(current_obj, obj_id, obj_class)
    
    def _process_target_object(self, current_obj, obj_id, x1, y1, x2, y2, frame):
        """Process objects that are in target classes"""
        prev_obj = self.previous_positions.get(obj_id, current_obj)
        
        # Draw bounding box and center point
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
        cv2.circle(frame, (int(current_obj.centerx), int(current_obj.centery)), 5, (0, 255, 0), -1)
        
        # Draw ID label
        label = f"ID: {obj_id}"
        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        
        # Check for line crossing
        self._check_line_crossing(current_obj, prev_obj, obj_id)
        
        # Update position tracking
        self._update_object_position(obj_id, current_obj)
    
    def _process_anomaly_object(self, current_obj, obj_id, obj_class):
        """Process objects that are not in target classes (anomalies)"""
        if obj_id not in self.anomaly_objects:
            self._log_anomaly(obj_class)
            current_obj.detect = True
            self.anomaly_objects[obj_id] = current_obj
    
    def _check_line_crossing(self, current_obj, prev_obj, obj_id):
        """Check if object crossed the virtual line"""
        if prev_obj == current_obj:
            return
            
        prev_coord = prev_obj.centery if self.is_horizontal_line else prev_obj.centerx
        current_coord = current_obj.centery if self.is_horizontal_line else current_obj.centerx
        virtual_line_pos = self.line_y if self.is_horizontal_line else self.line_x
        
        # Check if object crossed the line (from above/left to below/right)
        if (prev_coord < virtual_line_pos) and (current_coord >= virtual_line_pos):
            if not prev_obj.detect:
                self.obj_count += 1
            prev_obj.detect = True
            
            # Record time between crossings
            current_time = time.time()
            if (current_time - self.last_cross_time > self.cross_threshold):
                self.time_between_crossings.append(current_time - self.last_cross_time)
            self.last_cross_time = current_time
    
    def _update_object_position(self, obj_id, current_obj):
        """Update object position in tracking dictionary"""
        if obj_id not in self.previous_positions:
            self.previous_positions[obj_id] = current_obj
        else:
            tracked_obj = self.previous_positions[obj_id]
            tracked_obj.centerx = current_obj.centerx
            tracked_obj.centery = current_obj.centery
            self.previous_positions[obj_id] = tracked_obj
    
    def _log_anomaly(self, obj_class):
        """Log anomaly detection to file"""
        with open(self.output_log_path, "a") as f:
            f.write(f"An anomaly '{self.model.names[int(obj_class)]}' was detected on the line at {time.ctime(time.time())}\n")
    
    def analyze_system_status(self):
        """Analyze system status based on object count"""
        current_time = time.time()
        if (current_time - self.start_time) < self.time_threshold:
            return None
            
        readable_time = time.ctime(current_time)
        functioning = True
        
        print(f"Object count in time window: {self.obj_count}")
        
        # Determine system status
        if self.obj_count >= (self.obj_per_time - self.bounds) and self.obj_count <= (self.obj_per_time + self.bounds):
            if not status.functioning:
                self._log_status("Returned to normal operation", readable_time)
            functioning = True
        elif self.obj_count > (self.obj_per_time + self.bounds):
            self._log_status("Too Fast", readable_time)
            functioning = False
        elif self.obj_count < (self.obj_per_time - self.bounds) and self.obj_count > 0:
            self._log_status("Too Slow", readable_time)
            functioning = False
        else:
            self._log_status("Stopped", readable_time)
            functioning = False
        
        # Notify backend if status changed
        self._notify_status_change(functioning)
        
        # Reset counters
        self.obj_count = 0
        self.start_time = current_time
        
        return functioning
    
    def _log_status(self, status_msg, timestamp):
        """Log status change to file"""
        with open(self.output_log_path, "a") as f:
            f.write(f"{status_msg} on {timestamp}\n")
    
    def _notify_status_change(self, functioning):
        """Notify backend of status change"""
        print(f"🔄 Current status: {functioning}, Global status: {status.functioning}")
        
        if functioning != status.functioning:
            try:
                print(f"🔄 Notifying backend of status change: {functioning}")
                status.functioning = functioning
                print(f"After status change - Current: {functioning}, Global: {status.functioning}")
                
                # Send request to backend
                requests.post(
                    "http://localhost:8001/internal-update-status", 
                    json={"functioning": functioning}
                )
            except Exception as e:
                print(f"❌ Failed to notify backend: {e}")
    
    def add_frame_overlay(self, frame):
        """Add overlay information to frame"""
        cv2.putText(frame, f"Count: {self.obj_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    def get_crossing_statistics(self):
        """Get statistics about object crossings"""
        if len(self.time_between_crossings) > 1:
            return {
                "std_deviation": np.array(self.time_between_crossings).std(),
                "mean_time": np.array(self.time_between_crossings).mean(),
                "total_crossings": len(self.time_between_crossings)
            }
        return {"std_deviation": 0, "mean_time": 0, "total_crossings": 0}
    
    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        if self.out_video:
            self.out_video.release()
        cv2.destroyAllWindows()
    
    def run_monitoring(self, video_path, output_log_path, line_factor, is_horizontal_line, 
                      cross_threshold, targets, obj_per_time, time_threshold, bounds):
        """Main method to run the complete monitoring system"""
        # Initialize system
        self.configure_detection_parameters(targets, obj_per_time, time_threshold, bounds, output_log_path)
        self.cross_threshold = cross_threshold
        
        # Set up video processing
        width, height, fps = self.initialize_video_capture(video_path)
        self.setup_virtual_line(width, height, line_factor, is_horizontal_line)
        
        print(f"🎥 Starting monitoring - Resolution: {width}x{height}, FPS: {fps}")
        
        # Main processing loop
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            self.frame_count += 1
            
            if not ret:
                break
            
            # Detect objects
            results = self.detect_objects(frame)
            
            # Draw virtual line
            self.draw_virtual_line(frame, width, height)
            
            # Process detected objects
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                ids = results[0].boxes.id.cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                
                for box, obj_id, obj_class in zip(boxes, ids, classes):
                    self.process_detected_object(box, obj_id, obj_class, frame)
            
            # Add overlay information
            self.add_frame_overlay(frame)
            
            # Write processed frame
            self.out_video.write(frame)
            
            # Show preview
            display_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow("Live Preview", display_frame)
            
            # Analyze system status
            self.analyze_system_status()
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Print final statistics
        stats = self.get_crossing_statistics()
        print(f"📊 Final Statistics: {stats}")
        
        # Cleanup
        self.cleanup()


def OperationStatus(video_path, out_path, line, factor, cross_threshold, targets, obj_per_time, time_th, bounds):
    """Legacy function wrapper for backward compatibility"""
    vision_system = ConveyorVisionSystem()
    vision_system.run_monitoring(
        video_path=video_path,
        output_log_path=out_path,
        line_factor=factor,
        is_horizontal_line=line,
        cross_threshold=cross_threshold,
        targets=targets,
        obj_per_time=obj_per_time,
        time_threshold=time_th,
        bounds=bounds
    )
