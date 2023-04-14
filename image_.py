import cv2
import time
import logging

def obtain_image():
    logging.info("Image_      : creating image")

    video = cv2.VideoCapture(0)

    output = []

    frame_number = 0
    while True:
        ret, frame = video.read()

        cv2.imshow('frame', frame)

        # Keep track of the frame number and the time
        frame_number += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()