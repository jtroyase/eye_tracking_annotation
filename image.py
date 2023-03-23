import cv2
import threading
import time

class VideoRecorder(threading.Thread):
    def __init__(self):
        super().__init__()
        self.video = cv2.VideoCapture(0)

        self.is_running = True
        self.output = []
  
    def run(self):
        self.frame_number = 0
        while self.is_running:
            ret, frame = self.video.read()

            cv2.imshow('frame', frame)

            # Keep track of the frame number and the time
            self.output.append((time.time(), self.frame_number))
            self.frame_number += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_running = False
                print(self.output)
                break
        self.video.release()
        cv2.destroyAllWindows()