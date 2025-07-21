## To run the tracking using ocsort
### Mac/linux
#### mkdir -p .config/ultralytics/trackers
#### 

# make new file in the newly created foler .config/ultralytics/trackers
## Copy into it the following:

##### tracker_type: ocsort
##### appearance: True
##### match_thresh: 0.3
##### track_buffer: 100
##### proximity_thresh: 0.1
##### min_box_area: 10
##### vertical_ratio: 1.6
##### iou_thresh: 0



## And save