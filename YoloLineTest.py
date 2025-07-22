import cv2
import time
from ultralytics import YOLO
import json
import numpy as np
from dataclasses import dataclass
import status 
import requests

@dataclass
class object:
    centerx: float
    centery: float
    detect: bool

def OperationStatus(video_path, out_path, line, factor, cross_threshold, targets, obj_per_time, time_th, bounds):
    # global functioning 
    cap = cv2.VideoCapture(video_path)
    model = YOLO("Our_Models/Best_Models/bestdet.pt") 

    # output video writer setup
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize VideoWriter to save the processed video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
    output_video_path = 'output_processed.mp4'  # or take this as a parameter
    out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # vertical line position (middle of frame but can tweak it a lot)
    line_x = int(width * factor)
    line_y = int(height * factor)
    last_cross_time = time.time()
    start_time = time.time()

    time_between_crossings = []
    obj_count = 0
    frame_count = 0
    previous_positions = {}
    anamoly = {} # objects that are not in the target classes but are detected on the line

    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1
        if not ret:
            break

        results = model.track(source=frame, conf=0.1, iou=0.5, show=False, persist=True, tracker="botsort.yaml", verbose = False)

        # Draw the virtual line (visualization)
        if line:  # horizontal line
            cv2.line(frame, (0, line_y), (width, line_y), (0, 0, 255), 2)
        else:  # vertical line
            cv2.line(frame, (line_x, 0), (line_x, height), (0, 0, 255), 2)

        if results[0].boxes.id != None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            IDs = results[0].boxes.id.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            
            for box, Id, clas in zip(boxes, IDs, classes):
                obj_id = Id
                x1, y1, x2, y2 = box
            
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                obj = object(cx, cy, False)
                

                if clas in targets:
                    prev = previous_positions.get(obj_id, obj)
                    # drawing the bounding boxes and the ID Labels
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                    label = f"ID: {obj_id}"
                    cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

                    prevc = prev.centery if line else prev.centerx
                    center = cy if line else cx
                    vir_line = line_y if line else line_x

                    if prev != obj:
                        if (prevc < vir_line) and (center >= vir_line):
                            if prev.detect == False:
                                obj_count += 1
                            prev.detect = True
                            if (time.time() - last_cross_time > 0.5):
                                time_between_crossings.append(time.time() - last_cross_time)
                            last_cross_time = time.time()
                    
                    if previous_positions.get(obj_id) == None:
                        previous_positions[obj_id] = obj
                    else:
                        temp_obj = previous_positions[obj_id]
                        temp_obj.centerx = obj.centerx
                        temp_obj.centery = obj.centery
                        previous_positions[obj_id] = temp_obj
                else:
                    if anamoly.get(obj_id) == None:
                        with open(out_path, "a") as f:
                            f.write(f"a {model.names[int(clas)]} was detected on the line at {time.ctime(time.time())}\n")
                        obj.detect = True
                        anamoly[obj_id] = obj
                    # we should also consider the case where the object is not in the target classes but has already been detected
                    #  so we can log it as an anamoly
                    #  else: 
                    #     with open(out_path, "a") as f:
                    #         f.write(f"a {model.names[int(clas)]} was detected on the line at {time.ctime(time.time())}\n")
                    #     obj.detect = True
                    #     anamoly[obj_id] = obj
        
        # Display object count on frame
        cv2.putText(frame, f"Count: {obj_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Write the processed frame to output video
        out_video.write(frame)
        
        # Show the preview window
        display_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Scale down to 50%

        cv2.imshow("Live Preview", display_frame)

        if time.time() - start_time >= time_th:
            readable_time = time.ctime(time.time())
            print(obj_count)
            if obj_count >= obj_per_time - bounds and obj_count <= obj_per_time + bounds:
                if status.functioning == False:
                    with open(out_path, "a") as f:
                        f.write(f"Returned to normal operation on {readable_time}\n")
                functioning = True
            elif obj_count > obj_per_time + bounds:
                with open(out_path, "a") as f:
                    f.write(f"Too Fast on {readable_time}\n")
                functioning = False
            elif obj_count < obj_per_time - bounds and obj_count > 0:
                with open(out_path, "a") as f:
                    f.write(f"Too Slow on {readable_time}\n")
                functioning = False
            else:
                with open(out_path, "a") as f:
                    f.write(f"Stopped on {readable_time}\n")
                functioning = False

            print("🔄 status :", functioning, "while global is ", status.functioning)
            if functioning != status.functioning:
                try:
                    print("🔄 Notifying backend of status change:", functioning, "while global is ", status.functioning)
                    status.functioning = functioning
                    print("after status change:", functioning, "while global is ", status.functioning)
                    # The request is commented as it does not reflect the change that the api does to functioning to this function so for now we change it here 
                    requests.post("http://localhost:8001/internal-update-status", json={"functioning": functioning}) # chnage the local host accordingly
                except Exception as e:
                    print("❌ Failed to notify backend:", e)
            print(functioning)
            obj_count = 0
            start_time = time.time()

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(np.array(time_between_crossings).std())

    # Release resources
    cap.release()
    out_video.release()
    cv2.destroyAllWindows()


# Chatgpt suggestion

# if functioning != status.functioning:
#     try:
#         print("🔄 Notifying backend of status change:", functioning)
#         response = requests.post(
#             "http://localhost:8001/internal-update-status",
#             json={"functioning": functioning}
#         )
#         result = response.json()
#         if result["updated"]:
#             status.functioning = result["functioning"]
#     except Exception as e:
#         print("❌ Failed to notify backend:", e)
