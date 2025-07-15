## To run the tracking using the ocsort
### Mac/linux
#### mkdir -p ~/.config/ultralytics/trackers
#### nano ~/.config/ultralytics/trackers/botsort.yaml  , use this then write the following in it
##### tracker_type: ocsort
##### appearance: True
##### match_thresh: 0.3
##### track_buffer: 100
##### proximity_thresh: 0.1
##### min_box_area: 10
##### vertical_ratio: 1.6
##### iou_thresh: 0
