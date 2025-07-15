import cv2
import time
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import json
import numpy as np
from dataclasses import dataclass

@dataclass
class object:
    center: float
    detect: bool


# Load the video
video_path = "coffee.mp4"
cap = cv2.VideoCapture(video_path)
model = YOLO("detect.pt")


# output video writer
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
out = cv2.VideoWriter('outcoffee.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# vertiical line position (middle of frame but can tweak it a lot)
line_x = int(width * 0.5)

# Initialize time and threshold for product movement would change depending on machine normal
last_cross_time = time.time()
#loading calibration data
# with open('calibration.json', 'r') as f:
#     calibration_data = json.load(f)

# # Extract threshold from calibration data
# cross_threshold = calibration_data.get("threshold", 3)
cross_threshold = 4

prev_centroids = []
avg_time = 0.0
# objects_detected = 0
time_between_crossings = []
obj_count = 0
frame_count = 0
# dictionary that stores the movements of all the objects detected
previous_positions = {}

while cap.isOpened():
    ret, frame = cap.read()
    frame_count += 1
    if not ret:
        break

    # class for the object detected
    # Box: 0, Fruit: 1, bag: 2, bottle: 3, jar: 4, mask: 5, pallet: 6
    TARGET_CLASSES = [2]

    results = model.track(source=frame, conf=0.1, iou=0.5, show=False, persist = True,tracker = "botsort.yaml")

    # gets the dimensions , id , and class for all objects detected in a frame
    boxes = results[0].boxes.xyxy.cpu().numpy()
    IDs = results[0].boxes.id.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    
    for box, Id, clas in zip(boxes, IDs,classes):
        if clas == TARGET_CLASSES:

            # gets the id and dimensions for the first object detected
            obj_id = Id
            x1, y1, x2, y2 = box
    
            # calculates the center coordinates
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # creates a new object
            obj = object(cx,False)
            # getting the previous postion of that object
            prev_x = previous_positions.get(obj_id,obj)

            # drawing the bounding boxes and the ID Labels
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            label = f"ID: {obj_id}"
            cv2.putText(frame,label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0, 0, 255),2,cv2.LINE_AA)

            # only tracks movement if the object was detected before
            if prev_x != obj:
                if prev_x.center < line_x and cx >= line_x:
                    # counts the object before getting detected
                    if obj.detect == False:
                        obj_count += 1
                    obj.detect = True
                    # gets the time between each object passing
                    if (time.time() - last_cross_time > 1):  # Avoid multiple crossings in a short time
                        time_between_crossings.append(time.time() - last_cross_time)
                    last_cross_time = time.time()
            
            # checks if the object was stored if not it stores it
            if previous_positions.get(obj_id) == None:
                previous_positions[obj_id] = obj
            # changes only the center of the object in the dictonary
            else:
                temp_obj = previous_positions[obj_id]
                temp_obj.center = obj.center
                previous_positions[obj_id] = temp_obj

    # Draw vertical line
    cv2.line(frame, (line_x, 0), (line_x, height), (0, 0, 255), 2)

#     # Calculate time since last crossing
    time_since_last_cross = time.time() - last_cross_time
    production_status = "Running" if time_since_last_cross < cross_threshold else "Waiting" if time_since_last_cross >= cross_threshold and time_since_last_cross < cross_threshold*3  else "Stopped"
    color = (0, 255, 0) if production_status == "Running" else (0, 255, 255) if production_status == "Waiting" else (0, 0, 255)

#     # Display status
    cv2.putText(frame, f"Production: {production_status}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    
    cv2.putText(frame, f"Number of objects: {obj_count}", (1500, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    cv2.putText(frame, f"Time since last object: {time_since_last_cross:.2f}", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    
    if obj_count > 0:
        avg_time = sum(time_between_crossings) / len(time_between_crossings)

    cv2.putText(frame, f"Avg Time Between Crossings: {avg_time:.2f}", (30, 180),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)


    out.write(frame)

print(np.array(time_between_crossings).std())


cap.release()
out.release()
