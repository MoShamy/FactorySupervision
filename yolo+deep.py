import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

# Load YOLOv8 model
model = YOLO("models/yolov8l.pt")  # or yolov8x.pt for higher accuracy


# Load video
video_path = "testVid/test_vid_2.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

# For speed tracking
prev_positions = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]

    # Run YOLOv8 detection
    results = model(frame, imgsz=960, conf=0.3, verbose=False)[0]

    detections = []
    for box, conf, cls in zip(results.boxes.xyxy, results.boxes.conf, results.boxes.cls):
        x1, y1, x2, y2 = map(int, box)
        detections.append(([x1, y1, x2 - x1, y2 - y1], conf.item(), cls.item()))

    # Update DeepSORT with current detections
    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = track.to_ltrb()
        x1, y1, x2, y2 = int(l), int(t), int(l + w), int(t + h)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Speed calculation
        speed = 0
        if track_id in prev_positions:
            px, py = prev_positions[track_id]
            dist = np.linalg.norm([cx - px, cy - py])
            speed = dist * fps  # pixels/second
        prev_positions[track_id] = (cx, cy)

        # Draw bounding box and speed label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"ID {track_id} | {speed:.1f}px/s"
        cv2.putText(frame, label, (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

    # Show result
    cv2.imshow("YOLOv8 + DeepSORT Tracking", frame)
    if cv2.waitKey(21) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
