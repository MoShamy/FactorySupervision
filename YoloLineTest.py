import cv2
import time
from ultralytics import YOLO
import json
import numpy as np
from dataclasses import dataclass

@dataclass
class object:
    centerx: float
    centery: float
    detect: bool


# Load the video
video_path = "/Users/mostafa/Desktop/FactorySupervision/Dataset/Video/test_vid_2.mp4"
cap = cv2.VideoCapture(video_path)
model = YOLO("Our_Models/Model2/model2.pt") 


# output video writer
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
out = cv2.VideoWriter('outbox1.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# vertiical line position (middle of frame but can tweak it a lot)
line_x = int(width * 0.35)
line_y = int(height * 0.2)

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
total = 20
bar_chart = "["
bar_chart += "░" * total  + "]"  # Initialize with 10 zeros

print("Starting video processing...")
while cap.isOpened():
    progress = (frame_count / int(cap.get(cv2.CAP_PROP_FRAME_COUNT))) * total
    bar_chart = "[" + "█" * int(progress) + "░" * (total - int(progress)) + "]"
    print(f"Progress: {bar_chart} {frame_count + 1}/{int(cap.get(cv2.CAP_PROP_FRAME_COUNT))} frames processed", end="\r")
    ret, frame = cap.read()
    frame_count += 1
    if not ret:
        break 

    # class for the object detected
    # Box: 0, Fruit: 1, bag: 2, bottle: 3, jar: 4, mask: 5, pallet: 6
    TARGET_CLASSES = [0, 1, 2, 3, 4, 5, 6]  # Adjust this list based on your target classes

    results = model.track(source=frame, conf=0.1, iou=0.5, show=False, persist = True,tracker = "botsort.yaml",verbose= False)

    # gets the dimensions , id , and class for all objects detected in a frame
    boxes = results[0].boxes.xyxy.cpu().numpy()
    IDs = results[0].boxes.id.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    
    for box, Id, clas in zip(boxes, IDs,classes):
        if clas in TARGET_CLASSES:  # Check if the class is in the target classes

            # gets the id and dimensions for the first object detected
            obj_id = Id
            x1, y1, x2, y2 = box
    
            # calculates the center coordinates
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # creates a new object 
            obj = object(cx,cy,False)
            # getting the previous postion of that object
            prev = previous_positions.get(obj_id,obj)

            # drawing the bounding boxes and the ID Labels
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            label = f"ID: {obj_id}"
            cv2.putText(frame,label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0, 0, 255),2,cv2.LINE_AA)

            # only tracks movement if the object was detected before
            # Only track if the object has moved
            if prev.centerx != obj.centerx or prev.centery != obj.centery:
                # Check if the object crosses the line for the first time
                crossed_line = (
                    (prev.centerx < line_x and cx >= line_x) or
                    (prev.centery < line_y and cy >= line_y)
                )

                if crossed_line and not prev.detect:
                    # Count the object
                    obj_count += 1
                    prev.detect = True

                    # Record time since last valid crossing
                    current_time = time.time()
                    time_between = current_time - last_cross_time

                    if time_between > 0.5:  # Avoid micro bounces
                        time_between_crossings.append(time_between)
                        last_cross_time = current_time

            
            # checks if the object was stored if not it stores it
            if previous_positions.get(obj_id) == None:
                previous_positions[obj_id] = obj
            # changes only the center of the object in the dictonary 
            else:
                temp_obj = previous_positions[obj_id]
                temp_obj.centerx = obj.centerx
                temp_obj.centery = obj.centery
                previous_positions[obj_id] = temp_obj

    # Draw vertical line
    cv2.line(frame, (line_x,0), (line_x, height), (0, 0, 255), 2)

     # Calculate time since last crossing
    time_since_last_cross = time.time() - last_cross_time
    production_status = "Running" if time_since_last_cross < cross_threshold else "Waiting" if time_since_last_cross >= cross_threshold and time_since_last_cross < cross_threshold*3  else "Stopped"
    color = (0, 255, 0) if production_status == "Running" else (0, 255, 255) if production_status == "Waiting" else (0, 0, 255)

     # Display status
    cv2.putText(frame, f"Production: {production_status}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    
    cv2.putText(frame, f"Number of objects: {obj_count}", (1500, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    cv2.putText(frame, f"Time since last object: {time_since_last_cross:.2f}", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    
    # if obj_count > 0:
    #     avg_time = sum(time_between_crossings) / len(time_between_crossings)

    # cv2.putText(frame, f"Avg Time Between Crossings: {avg_time:.2f}", (30, 180),
    #     cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)


    out.write(frame)

print(np.array(time_between_crossings).std())


cap.release()
out.release()