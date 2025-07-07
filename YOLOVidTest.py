from ultralytics import YOLO
import cv2
import supervision as sv
import numpy as np
import time

# Load YOLOv8 model
model = YOLO("models/yolov8m.pt") 

# Open video file
video_path = "vidDatasets/test_vid_2.mp4"
cap = cv2.VideoCapture(video_path)

# Initialize tracker
tracker = sv.ByteTrack()  # You can switch to StrongSORT with more config

# For speed tracking
object_speeds = {}
object_last_positions = {}
object_last_times = {}

frame_rate = cap.get(cv2.CAP_PROP_FPS)
print(f"Video FPS: {frame_rate}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)

    # Update tracker
    detections = tracker.update_with_detections(detections)

    current_time = time.time()

    for i, (xyxy, track_id) in enumerate(zip(detections.xyxy, detections.tracker_id)):
        if track_id is None:
            continue

        x1, y1, x2, y2 = map(int, xyxy)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Compute speed
        if track_id in object_last_positions:
            prev_pos = object_last_positions[track_id]
            prev_time = object_last_times[track_id]
            distance = np.linalg.norm(np.array((cx, cy)) - np.array(prev_pos))
            dt = current_time - prev_time
            speed = distance / dt  # pixels per second

            object_speeds[track_id] = speed

        object_last_positions[track_id] = (cx, cy)
        object_last_times[track_id] = current_time

        # Draw box
        label = f"ID {track_id} | {object_speeds.get(track_id, 0):.1f} px/s"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow("YOLOv8 Tracking", frame)
    if cv2.waitKey(1) == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
