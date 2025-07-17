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

 # Box: 0, Fruit: 1, bag: 2, bottle: 3, jar: 4, mask: 5, pallet: 6
 # video_path: for the input video stream 
 # out_path: for the log
 # line: boolean used to see if we are using a vertical or horizotal line
 # factor: what will be multiplied with either the eidth of height for the line
 # cross_threshold: the time before the process is considered to have stopped
 # targets: a list containing the target classes
 # obj_per_time: the usual object per specific time produced in production
 # time_th: Minimum time that has to pass before checking the state of operation
 # bounds: the margin of error allowed for the number of products produced
def OperationStatus(video_path,out_path,line,factor,cross_threshold,targets,obj_per_time,time_th,bounds):

    cap = cv2.VideoCapture(video_path)
    model = YOLO("bestdet.pt") 

    # output video writer
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = int(cap.get(cv2.CAP_PROP_FPS))
    # out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # vertiical line position (middle of frame but can tweak it a lot)
    line_x = int(width * factor)
    line_y = int(height * factor)
    last_cross_time = time.time()
    start_time = time.time()

    avg_time = 0.0
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

        results = model.track(source=frame, conf=0.1, iou=0.5, show=False, persist = True,tracker = "botsort.yaml")

        if results[0].boxes.id != None :
            # gets the dimensions , id , and class for all objects detected in a frame
            boxes = results[0].boxes.xyxy.cpu().numpy()
            IDs = results[0].boxes.id.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            
            for box, Id, clas in zip(boxes, IDs,classes):
                if clas in targets:
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

                    prevc = prev.centery if line else prev.centerx
                    center = cy if line else cx
                    vir_line = line_y if line else line_x

                    # only tracks movement if the object was detected before
                    if prev != obj:
                        if (prevc < vir_line ) and (center >= vir_line ):
                            # counts the object before getting detected
                            if prev.detect == False:
                                obj_count += 1
                            prev.detect = True
                            # gets the time between each object passing
                            if (time.time() - last_cross_time > 0.5):  # Avoid multiple crossings in a short time   
                                time_between_crossings.append(time.time() - last_cross_time)
                            last_cross_time = time.time()
                    
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
        # if line:
        #      cv2.line(frame, (0,line_y), (width, line_y), (0, 0, 255), 2)
        # else:
        #     cv2.line(frame, (line_x,0), (line_x, height), (0, 0, 255), 2)

    #     # Calculate time since last crossing
        # time_since_last_cross = time.time() - last_cross_time
        # production_status = "Running" if time_since_last_cross < cross_threshold else "Waiting" if time_since_last_cross >= cross_threshold and time_since_last_cross < cross_threshold*3  else "Stopped"
        # color = (0, 255, 0) if production_status == "Running" else (0, 255, 255) if production_status == "Waiting" else (0, 0, 255)

        #checks which the production is currently in
        if start_time - time.time() >= time_th:
            readable_time = time.ctime(time.time())
            if obj_count >= obj_per_time - bounds and obj_count <= obj_per_time + bounds:
                with open(out_path, "a") as f:
                    f.write(f"Running on {readable_time}")
            elif obj_count > obj_per_time + bounds:
                with open(out_path, "a") as f:
                    f.write(f"Too Fast on {readable_time}")
            elif obj_count < obj_per_time - bounds and obj_count > 0:
                with open(out_path, "a") as f:
                    f.write(f"Too Slow on {readable_time}")
            else:
                with open(out_path, "a") as f:
                    f.write(f"Stopped on {readable_time}")

            obj_count = 0
            start_time = time.time()

    # #     # Display status
    #     cv2.putText(frame, f"Production: {production_status}", (30, 60),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        
    #     cv2.putText(frame, f"Number of objects: {obj_count}", (30, 200),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    #     cv2.putText(frame, f"Time since last object: {time_since_last_cross:.2f}", (30, 120),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        
        # if obj_count > 0:
        #     avg_time = sum(time_between_crossings) / len(time_between_crossings)

        # cv2.putText(frame, f"Avg Time Between Crossings: {avg_time:.2f}", (30, 180),
        #     cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)


        # out.write(frame)
    print(np.array(time_between_crossings).std())


    cap.release()
    #out.release()
