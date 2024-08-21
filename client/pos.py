from ultralytics import YOLO
from collections import defaultdict
import supervision as sv
import cv2
import numpy as np
import socketio
import json

class Pos:
    def __init__(self, webcam):
        self.model = YOLO("best-m401.pt")
        # self.model = YOLO("YOLOv8s_200+200+5n_best.pt")
        
        self.cap = cv2.VideoCapture(webcam)
        self.capwidth = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.capheight = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.start_point= (int(self.capwidth/2), 0)
        self.end_point = (int(self.capwidth/2), int(self.capheight))
        self.tid_status = {}
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        self.sio.connect('http://localhost:3000')
        
    def detection(self):
        track_history = defaultdict(lambda: [])
        tracker = sv.ByteTrack()
        # box_annotator = sv.BoxAnnotator(thickness=8)
        round_box_annotator = sv.RoundBoxAnnotator(thickness=8)
        label_annotator = sv.LabelAnnotator( text_scale=3, text_thickness=1, text_padding=10, text_position=sv.Position.CENTER)
        
        tid_status = {}
        
        while self.cap.isOpened():
            success, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            
            if success:
                results = self.model(frame)[0]
                detections = sv.Detections.from_ultralytics(results)
                detections = tracker.update_with_detections(detections)

                if detections['class_name'] is not None:
                    self.chk_item_status(detections)
                    labels = [f"#{tracker_id} {class_name} {confidence:.2f}" for tracker_id, class_name,confidence in zip(detections.tracker_id,detections['class_name'], detections.confidence)]
                else:
                    labels = []
                    
                annotated_frame = round_box_annotator.annotate(scene=frame.copy(), detections=detections)
                annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
                cv2.line(annotated_frame, self.start_point, self.end_point, (0, 255, 0), 2)
                cv2.imshow('Webcam', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break
        self.cap.release()
        cv2.destroyAllWindows()
        self.sio.disconnect()
    
    def chk_item_status(self, detections):
        for tid, classid, xyxy, classname in zip(detections.tracker_id, detections.class_id, detections.xyxy, detections['class_name']):
            if tid in self.tid_status:
                if self.tid_status[tid] == 2 : continue
                if (xyxy[0] < self.start_point[0]) and (self.tid_status[tid] == 0):
                    self.tid_status[tid] = 1
                elif (int(((xyxy[0]+xyxy[2])/2)) > self.start_point[0]) and (self.tid_status[tid] == 1):
                    self.tid_status[tid] = 2  #pass to buy
                    self.socketio_emit(int(classid))
            else:
                self.tid_status[tid] = 0 
        print(self.tid_status)
    
    def socketio_emit(self, classid):   
        self.sio.emit('new_item_from_pos',int(classid))

if __name__ == '__main__':
    pos = Pos(1)  # 0:webcam1 / 1:webcam2
    pos.detection()