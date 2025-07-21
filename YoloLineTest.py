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

global functioning 
functioning = True

def OperationStatus(video_path,out_path,line,factor,cross_threshold,targets,obj_per_time,time_th,bounds):
    global functioning 
    
    cap = cv2.VideoCapture(video_path)
    model = YOLO("/Users/mostafa/Desktop/FactorySupervision/Our_Models/Model2/model2.pt") 

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"❌ Error: Could not open video file {video_path}")
        return None

    # output video writer
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"📹 Video Info: {width}x{height} @ {fps} FPS")
    print(f"📊 Total frames: {total_frames}, Duration: {duration:.2f} seconds")
    
    # Create output video filename based on input
    import os
    input_name = os.path.splitext(os.path.basename(video_path))[0]
    output_video_path = f"Results/Processed_Videos/{input_name}_processed.mp4"
    os.makedirs("Results/Processed_Videos", exist_ok=True)
    
    # Initialize video writer with better codec settings
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Try mp4v first
    out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    # Check if video writer opened successfully
    if not out_video.isOpened():
        print("⚠️ Warning: mp4v codec failed, trying XVID...")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_video_path = output_video_path.replace('.mp4', '.avi')
        out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
    if not out_video.isOpened():
        print("❌ Error: Could not initialize video writer")
        cap.release()
        return None
    
    print(f"✅ Video writer initialized successfully")
    
    # Initialize OpenCV window for real-time display
    cv2.namedWindow("YOLO Line Detection", cv2.WINDOW_AUTOSIZE)
    print("🎥 Starting real-time video stream... Press 'q' to quit, 'p' to pause")
    print(f"💾 Output video will be saved to: {output_video_path}")

    # Calculate frame delay for real-time playback
    frame_delay = int(1000 / fps) if fps > 0 else 33  # milliseconds per frame
    print(f"⏱️ Frame delay: {frame_delay}ms for {fps} FPS playback")

    # vertiical line position (middle of frame but can tweak it a lot)
    line_x = int(width * factor)
    line_y = int(height * factor)
    last_cross_time = time.time()
    start_time = time.time()
    process_start_time = time.time()

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
            print(f"📹 End of video reached or failed to read frame {frame_count}")
            break

        results = model.track(source=frame, conf=0.1, iou=0.5, show=False, persist = True,tracker = "botsort.yaml", verbose=False)

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
        
        # Draw the detection line on the frame
        if line:  # Horizontal line
            cv2.line(frame, (0, line_y), (width, line_y), (0, 0, 255), 3)
        else:  # Vertical line
            cv2.line(frame, (line_x, 0), (line_x, height), (0, 0, 255), 3)
        
        # Add production status text on frame
        current_time = time.time()
        time_since_last = current_time - last_cross_time
        if time_since_last < cross_threshold:
            status_text = "Running"
            status_color = (0, 255, 0)  # Green
        elif time_since_last < cross_threshold * 3:
            status_text = "Waiting"
            status_color = (0, 255, 255)  # Yellow
        else:
            status_text = "Stopped"
            status_color = (0, 0, 255)  # Red
        
        # Add frame info and progress
        progress_percent = (frame_count / total_frames * 100) if total_frames > 0 else 0
        elapsed_time = current_time - process_start_time
        
        cv2.putText(frame, f"Status: {status_text}", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, status_color, 3)
        cv2.putText(frame, f"Objects: {obj_count}", (30, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time since last: {time_since_last:.1f}s", (30, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Frame: {frame_count}/{total_frames} ({progress_percent:.1f}%)", (30, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        cv2.putText(frame, f"Processing time: {elapsed_time:.1f}s", (30, 210), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        # Write the frame to output video (ALWAYS save)
        out_video.write(frame)
        
        # Display the frame in real-time
        cv2.imshow("YOLO Line Detection", frame)
        
        # Dynamic frame delay based on original video FPS
        key = cv2.waitKey(frame_delay) & 0xFF
        if key == ord('q'):
            print("🛑 User requested to quit...")
            break
        elif key == ord('p'):  # Pause functionality
            print("⏸️ Paused. Press any key to continue...")
            cv2.waitKey(0)
        elif key == ord('s'):  # Skip ahead
            print("⏭️ Skipping 10 frames...")
            for _ in range(10):
                ret, _ = cap.read()
                if not ret:
                    break
                frame_count += 10
            
        # Progress update every 30 frames
        if frame_count % 30 == 0:
            print(f"📹 Processing frame {frame_count}/{total_frames} ({progress_percent:.1f}%) - {status_text}")
            
        if not functioning:
            print("❌ Operation stopped due to malfunction.")
            break

        if  time.time() - start_time >= time_th:
            readable_time = time.ctime(time.time())
            if obj_count >= obj_per_time - bounds and obj_count <= obj_per_time + bounds:
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

            obj_count = 0
            start_time = time.time()




    print(f"📊 Processing completed:")
    print(f"   • Total frames processed: {frame_count}")
    print(f"   • Objects detected: {len(time_between_crossings)}")
    if len(time_between_crossings) > 0:
        print(f"   • Average time between crossings: {np.mean(time_between_crossings):.2f}s")
        print(f"   • Standard deviation: {np.array(time_between_crossings).std():.2f}s")

    cap.release()
    out_video.release()
    cv2.destroyAllWindows()  # Close all OpenCV windows
    
    print(f"✅ Real-time processing completed!")
    print(f"💾 Annotated video saved to: {output_video_path}")
    
    # Verify output video was created successfully
    if os.path.exists(output_video_path):
        file_size = os.path.getsize(output_video_path) / (1024 * 1024)  # MB
        print(f"📁 Output file size: {file_size:.2f} MB")
    else:
        print("⚠️ Warning: Output video file was not created successfully")
    
    return output_video_path


def test_video_stream(video_path):
    """
    Simple test function to verify real-time video streaming works.
    Just displays the video without any processing.
    """
    print(f"🧪 Testing video stream for: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video file {video_path}")
        return False
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
    
    cv2.namedWindow("Video Stream Test", cv2.WINDOW_AUTOSIZE)
    print("🎥 Press 'q' to quit video test...")
    
    # Calculate proper frame delay
    frame_delay = int(1000 / fps) if fps > 0 else 33
    
    frame_count = 0
    start_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1
        
        if not ret:
            print(f"📹 End of video reached at frame {frame_count}")
            break
        
        # Add frame counter and timing info
        elapsed = time.time() - start_time
        progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
        
        cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Progress: {progress:.1f}%", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Time: {elapsed:.1f}s", (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Video Stream Test", frame)
        
        # Use proper frame timing
        if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
            print("🛑 User requested to quit test...")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Video stream test completed")
    return True


def test_video_with_output(video_path):
    """
    Test function that creates both real-time display and saves output video.
    """
    print(f"🧪 Testing video with output for: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video file {video_path}")
        return False
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
    
    # Setup output video
    import os
    input_name = os.path.splitext(os.path.basename(video_path))[0]
    output_video_path = f"Results/Processed_Videos/{input_name}_test_output.mp4"
    os.makedirs("Results/Processed_Videos", exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    if not out_video.isOpened():
        print("⚠️ Warning: mp4v failed, trying XVID...")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_video_path = output_video_path.replace('.mp4', '.avi')
        out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    cv2.namedWindow("Video Test with Output", cv2.WINDOW_AUTOSIZE)
    print(f"🎥 Press 'q' to quit. Output will be saved to: {output_video_path}")
    
    frame_delay = int(1000 / fps) if fps > 0 else 33
    frame_count = 0
    start_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1
        
        if not ret:
            print(f"📹 End of video reached at frame {frame_count}")
            break
        
        # Add annotations
        elapsed = time.time() - start_time
        progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
        
        cv2.putText(frame, f"TEST OUTPUT - Frame: {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Progress: {progress:.1f}%", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        # Save to output video
        out_video.write(frame)
        
        # Display real-time
        cv2.imshow("Video Test with Output", frame)
        
        if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
            print("🛑 User requested to quit test...")
            break
    
    cap.release()
    out_video.release()
    cv2.destroyAllWindows()
    
    if os.path.exists(output_video_path):
        file_size = os.path.getsize(output_video_path) / (1024 * 1024)
        print(f"✅ Test completed! Output saved: {output_video_path} ({file_size:.2f} MB)")
        return True
    else:
        print("❌ Test failed: Output video not created")
        return False
