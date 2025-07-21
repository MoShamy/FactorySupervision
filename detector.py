import cv2
import numpy as np
import threading
import time
import os
from collections import deque # For buffering frames
import asyncio
# from notifications import send_push_notification

# --- Global Variables for Communication ---
# Use a deque (double-ended queue) to store a buffer of frames for recording
# This allows us to grab frames *before* motion is confirmed.
FRAME_BUFFER_SIZE = 30 # Number of frames to buffer (e.g., 1 second at 30 FPS)
frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

# Flag to signal if motion is detected (for the API to check)
motion_detected_flag = False

# Queue to store paths of recorded videos, so the API can list them
recorded_videos_queue = deque()

# Lock for safely updating global variables
lock = threading.Lock()

# --- Motion Detector Class ---
class CameraMotionDetector(threading.Thread):
    def __init__(self, record_path="recordings", min_motion_area=1500, fps=30, resolution=(640, 480)):
        super().__init__()
        self.record_path = record_path
        self.min_motion_area = min_motion_area
        self.fps = fps
        self.resolution = resolution
        self.running = False
        self.video_writer = None
        self.recording_start_time = None
        self.record_duration_seconds = 2 # Length of video clip to record

        os.makedirs(record_path, exist_ok=True) # Ensure recordings directory exists

        # Font settings for the label (for the imshow window)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.font_thickness = 2
        self.label_position = (10, 30) # Top-left corner for the label

    def run(self):
        global motion_detected_flag, frame_buffer, recorded_videos_queue

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("MotionDetector: Error: Could not open webcam.")
            for i in range(1, 5): # Try indices 1, 2, 3, 4
                print(f"MotionDetector: Trying camera index {i}...")
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    print(f"MotionDetector: Successfully opened camera with index {i}")
                    break
                else:
                    print(f"MotionDetector: Failed to open camera with index {i}")
                    cap.release() # Release if it couldn't open
                    time.sleep(0.5) # Small delay before trying next
            
            if not cap or not cap.isOpened():
                print("MotionDetector: Persistent Error: Could not open any webcam. Exiting thread.")
                self.running = False
                return
            # --- End camera index testing loop ---

        # Set camera resolution (optional, might not be supported by all cameras)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        # Initialize background subtractor
        fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=1000, detectShadows=False)

        self.running = True
        print("MotionDetector: Camera loop started.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("MotionDetector: Failed to grab frame. Releasing camera.")
                break

            # Add current frame to buffer
            frame_buffer.append(frame.copy()) # Append a copy to avoid modification issues

            # Convert to grayscale and apply background subtraction
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fgmask = fgbg.apply(gray) # Apply to grayscale

            # Morphological operations
            fgmask = cv2.dilate(fgmask, None, iterations=2)
            fgmask = cv2.erode(fgmask, None, iterations=1) 
            
            # Find contours
            contours, _ = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            current_motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) < self.min_motion_area:
                    continue
                current_motion_detected = True
                # Draw bounding box for visual feedback on the frame
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2) # Yellow rectangle
                # No break here if you want to draw all detected motion contours,
                # but if you just care if *any* motion is detected, break is fine.
                # Keeping break for efficiency as you only need the flag
                break 

            with lock:
                motion_detected_flag = current_motion_detected

            # --- Add label to the displayed frame ---
            if current_motion_detected:
                label_text = "MOTION DETECTED"
                label_color = (0, 0, 255)  # Red (BGR format)
            else:
                label_text = "No Motion"
                label_color = (0, 255, 0)  # Green (BGR format)

            cv2.putText(frame, label_text, self.label_position, self.font, 
                        self.font_scale, label_color, self.font_thickness, cv2.LINE_AA)

            # --- Display the frames ---
            cv2.imshow('Motion Detector Live Feed', frame) # Renamed window for clarity
            cv2.imshow('Foreground Mask (Debugging)', fgmask) # Renamed window for clarity

            # --- Recording Logic (Unchanged) ---
            if current_motion_detected and self.video_writer is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                video_filename = os.path.join(self.record_path, f"motion_{timestamp}.mp4")
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                
                h, w, _ = frame.shape # Get actual frame resolution
                
                self.video_writer = cv2.VideoWriter(video_filename, fourcc, self.fps, (w, h))
                if not self.video_writer.isOpened():
                    print(f"MotionDetector: Error: Could not create video writer for {video_filename}")
                    self.video_writer = None 
                    continue
                
                self.recording_start_time = time.time()
                print(f"MotionDetector: Motion detected. Starting recording: {video_filename}")

                for buffered_frame in frame_buffer:
                    self.video_writer.write(buffered_frame)
                
            elif self.video_writer is not None:
                if time.time() - self.recording_start_time < self.record_duration_seconds:
                    self.video_writer.write(frame) 
                else:
                    self.video_writer.release()
                    print(f"MotionDetector: Recording finished: {video_filename}") # Simpler print
                    
                    last_recorded_file = video_filename # Use the pre-constructed filename
                    with lock:
                        recorded_videos_queue.append(last_recorded_file)
                    
                    self.video_writer = None
                    self.recording_start_time = None
                    print("MotionDetector: Video writer released.")
            
            # Small delay to avoid 100% CPU usage if not processing fast enough
            time.sleep(0.01) 

            # Check for 'q' key press to quit from the imshow window
            # This needs to be checked in the same thread that calls imshow
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("MotionDetector: 'q' pressed. Stopping camera loop.")
                self.running = False # Set running to False to exit loop
                break # Exit the while loop

        cap.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows() # Close all OpenCV windows
        print("MotionDetector: Camera loop stopped.")

    def stop(self):
        self.running = False

# You can test this independently if you wish, but it's meant to be used by FastAPI
if __name__ == "__main__":
    # Ensure a 'recordings' directory exists for testing
    if not os.path.exists("recordings"):
        os.makedirs("recordings")
        print("Created 'recordings' directory for standalone test.")

    detector = CameraMotionDetector(record_path="recordings", min_motion_area=1500)
    detector.start()
    try:
        # This main thread loop is now just for observing shared state,
        # the camera feed is handled by the detector thread's imshow.
        while True:
            with lock:
                motion_status = motion_detected_flag
                videos_in_queue = list(recorded_videos_queue)
                # recorded_videos_queue.clear() # Don't clear here if FastAPI is also using it, or clear conditionally

            # This printout will continue in the console
            # print(f"MAIN: Motion Status: {motion_status}") 
            if videos_in_queue:
                for video_path in videos_in_queue:
                    print(f"MAIN: New video recorded: {video_path}")
                with lock: # Clear only after processing to ensure main thread sees it
                    recorded_videos_queue.clear() 
            
            time.sleep(0.5) # Check status more frequently
    except KeyboardInterrupt:
        print("MAIN: KeyboardInterrupt detected. Stopping detector...")
        detector.stop()
        detector.join() # Wait for the thread to finish
        print("MAIN: Detector stopped.")