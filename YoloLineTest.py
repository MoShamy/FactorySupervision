import cv2
import time
from ultralytics import YOLO
import json
import numpy as np

# Load the video
video_path = "testVid/test_vid_2.mp4"
cap = cv2.VideoCapture(video_path)
model = YOLO("models/yolov8m.pt") 

# output video writer
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
out = cv2.VideoWriter('resultVid/output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# vertiical line position (middle of frame but can tweak it a lot)
line_x = int(width * 0.5)

# Initialize time and threshold for product movement would change depending on machine normal
last_cross_time = time.time()
#loading calibration data
with open('calibration.json', 'r') as f:
    calibration_data = json.load(f)

# Extract threshold from calibration data
cross_threshold = calibration_data.get("threshold", 3)

prev_centroids = []
avg_time = 0.0
objects_detected = 0
time_between_crossings = []



while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 inference
    results = model(frame, verbose=False)[0]

    # Get detections: boxes, confidences, class indices
    boxes = results.boxes.xyxy.cpu().numpy()
    scores = results.boxes.conf.cpu().numpy()
    classes = results.boxes.cls.cpu().numpy()

    curr_centroids = []
    crossed_this_frame = False

    

    # COCO bottle index
    TARGET_CLASSES = [39] #only targeting bottles

    for box, conf, cls in zip(boxes, scores, classes):
        if int(cls) in TARGET_CLASSES:
            x1, y1, x2, y2 = box
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            curr_centroids.append((cx, cy))

            # Draw bounding box and centroid
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            # Line crossing check (left to right)
            for pcx, pcy in prev_centroids:
                if pcx < line_x and cx >= line_x:
                    crossed_this_frame = True
    
                    if (time.time() - last_cross_time > 1):  # Avoid multiple crossings in a short time   
                        time_between_crossings.append(time.time() - last_cross_time)
                    objects_detected += 1
                    last_cross_time = time.time()

    # Draw vertical line
    cv2.line(frame, (line_x, 0), (line_x, height), (0, 0, 255), 2)

    # Calculate time since last crossing
    time_since_last_cross = time.time() - last_cross_time
    production_status = "Running" if time_since_last_cross < cross_threshold else "Stopped"
    color = (0, 255, 0) if production_status == "Running" else (0, 0, 255)

    # Display status
    cv2.putText(frame, f"Production: {production_status}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)

    cv2.putText(frame, f"Time since last object: {time_since_last_cross:.2f}", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
    
    if objects_detected > 0:
        avg_time = sum(time_between_crossings) / len(time_between_crossings)

    cv2.putText(frame, f"Avg Time Between Crossings: {avg_time:.2f}", (30, 180),
        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    prev_centroids = curr_centroids
    out.write(frame)
    cv2.imshow("YOLOv8 + DeepSORT Tracking", frame)

    if cv2.waitKey(21) & 0xFF == 27:  # ESC to quit
        break

print(np.array(time_between_crossings).std())


cap.release()
out.release()