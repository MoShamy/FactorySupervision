import cv2
import time
from ultralytics import YOLO
import numpy as np
from dataclasses import dataclass

@dataclass
class object:
    centerx: float
    centery: float
    detect: bool

# Load the video
video_folder_path = "Dataset/Video/"
# cap = cv2.VideoCapture(video_path)
model = YOLO("Our_Models/Model1_collab/model1.1.pt") 
SKIP_N = 1  # Skip every N frames for performance
results = model.track(
    source=frame,
    conf=0.1,
    iou=0.5,
    show=False,
    persist=True,
    tracker="botsort.yaml",
    verbose=True
)
for vid in video_folder_path:
    video_path = video_folder_path + vid
    cap = cv2.VideoCapture(video_path)

    # Output video writer
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    adjusted_fps = max(fps // SKIP_N, 1)  # Avoid 0 FPS


    out = cv2.VideoWriter('outboxSLAY_too.mp4', cv2.VideoWriter_fourcc(*'mp4v'), adjusted_fps, (width, height))

    # Line position
    line_x = int(width * 0.35)
    line_y = int(height * 0.2)

    last_cross_time = time.time()
    cross_threshold = 4

    previous_positions = {}
    time_between_crossings = []
    obj_count = 0
    frame_count = 0
    frames_written = 0
    total_bar = 20

    def write_vid(frame, status, obj_count, time_since_last_cross,color=(0, 255, 0)):
        cv2.putText(frame, f"Production: {status}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        cv2.putText(frame, f"Number of objects: {obj_count}", (1500, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        cv2.putText(frame, f"Time since last object: {time_since_last_cross:.2f}", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        out.write(frame)

    print("Starting video processing...")


    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % SKIP_N != 0:
            continue

        # Progress bar
        progress = (frame_count / int(cap.get(cv2.CAP_PROP_FRAME_COUNT))) * total_bar
        bar_chart = "[" + "█" * int(progress) + "░" * (total_bar - int(progress)) + "]"
        print(f"Progress: {bar_chart} {frame_count}/{int(cap.get(cv2.CAP_PROP_FRAME_COUNT))} frames processed", end="\r")

        # Run model
        results = model.track(
            source=frame,
            conf=0.1,
            iou=0.5,
            show=False,
            persist=True,
            tracker="botsort.yaml",
            verbose=False
        )

        # Skip if no valid results
        if not results or not hasattr(results[0], "boxes") or results[0].boxes is None:
            write_vid(frame, "No objects detected", 0, 0)
            frames_written += 1
            continue

        boxes_data = results[0].boxes
        if boxes_data.id is None or len(boxes_data) == 0:
            write_vid(frame, "No objects detected", 0, 0)
            frames_written += 1
            continue

        boxes = boxes_data.xyxy.cpu().numpy()
        IDs = boxes_data.id.cpu().numpy()
        classes = boxes_data.cls.cpu().numpy()

        # TARGET_CLASSES = [0, 1, 2, 3, 4, 5, 6]
        for box, obj_id, clas in zip(boxes, IDs, classes):
            # if clas not in TARGET_CLASSES:
            #     continue

            x1, y1, x2, y2 = box
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            obj = object(cx, cy, False)
            prev = previous_positions.get(obj_id, obj)

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"ID: {int(obj_id)}", (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            moved = prev.centerx != obj.centerx or prev.centery != obj.centery
            crossed = (
                (prev.centerx < line_x and cx >= line_x) or
                (prev.centery < line_y and cy >= line_y)
            )

            if moved and crossed and not prev.detect:
                obj_count += 1
                prev.detect = True
                current_time = time.time()
                delta = current_time - last_cross_time
                if delta > 0.5:
                    time_between_crossings.append(delta)
                    last_cross_time = current_time

            previous_positions[obj_id] = object(cx, cy, prev.detect)

        # Draw vertical line
        cv2.line(frame, (line_x, 0), (line_x, height), (0, 0, 255), 2)

        # Display production status
        time_since_last_cross = time.time() - last_cross_time
        if time_since_last_cross < cross_threshold:
            status, color = "Running", (0, 255, 0)
        elif time_since_last_cross < cross_threshold * 3:
            status, color = "Waiting", (0, 255, 255)
        else:
            status, color = "Stopped", (0, 0, 255)

        write_vid(frame, status, obj_count, time_since_last_cross,color)

        


    # Final stats
    print()
    if time_between_crossings:
        std_dev = np.std(time_between_crossings)
        print(f"Standard deviation of time between crossings: {std_dev:.2f} seconds")
    else:
        print("No valid crossings detected — cannot compute standard deviation.")



cap.release()
out.release()
cv2.destroyAllWindows()
