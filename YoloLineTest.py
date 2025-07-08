import cv2
import time
from ultralytics import YOLO


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
cross_threshold = 3  # seconds until it says "Stopped"

prev_centroids = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 inference
    results = model(frame)
    detections = results[0].boxes.xyxy.cpu().numpy()

    curr_centroids = []
    crossed_this_frame = False

    for x1, y1, x2, y2 in detections:
        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
        curr_centroids.append((cx, cy))

        # Draw bounding box and centroid
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        # Line crossing check (left to right)
        for pcx, pcy in prev_centroids:
            if pcx < line_x and cx >= line_x:
                crossed_this_frame = True
                last_cross_time = time.time()

    # Draw vertical line
    cv2.line(frame, (line_x, 0), (line_x, height), (0, 0, 255), 2)

    # Calculate time since last crossing
    time_since_last_cross = time.time() - last_cross_time
    production_status = "Running" if time_since_last_cross < cross_threshold else "Stopped"
    color = (0, 255, 0) if production_status == "Running" else (0, 0, 255)

    # Display status at thhe top-left corner
    cv2.putText(frame, f"Production: {production_status}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    # Update previous centroids
    prev_centroids = curr_centroids
    cv2.imshow("YOLOv8 Production Line Monitoring", frame)
    out.write(frame)

cap.release()
out.release()


