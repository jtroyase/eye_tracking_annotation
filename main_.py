import threading
import logging
import time
import speech_recognition as sr

import image_
import gaze_

# ----------------------- Configuring logging ----------------------------
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

# --------------------- Endoscope Image thread ---------------------------
# Start receive of image as a daemon
logging.info("Main        : before creating image thread")
image = threading.Thread(target=image_.obtain_image, daemon=True)
image.start()

# ----------------- Initialize Eye Tracking network ----------------------
eye_tracker = gaze_.EyeTracker()

# --------------------- Voice recognizer thread --------------------------

# Some configuration values:
index_microphone = 1
frequency_adjust_ambient_noise = 10 #seconds

# Initialize microphone
r = sr.Recognizer()
mic = sr.Microphone(index_microphone)
logging.info(f"Main        : using microphone: {sr.Microphone.list_microphone_names()[index_microphone]}")

# adjust for ambient noise
logging.info("Main        : start adjusting for ambient noise")
with mic as source:
    r.adjust_for_ambient_noise(source, duration=1)

last_ambient_noise_measurement = time.time()

logging.info("Main:       : Adjusted for ambient noise")

# Create on callback audio function
def callback_listen(recognizer, audio):
    logging.info("Main        : callback_listen begins")
    try:
        speech_as_text = recognizer.recognize_whisper(audio, model='tiny.en', language="english", translate=False)
        speech_as_text = speech_as_text.lower()
        print(speech_as_text)

        if speech_as_text.count("activate") > 0:
            eye_tracker.is_running = True
            activate_thread = threading.Thread(target=eye_tracker.obtain_gaze)
            activate_thread.start()
        elif speech_as_text.count("stop") > 0:
            eye_tracker.is_running = False
            eye_tracker.stop()
    except sr.UnknownValueError:
        print("Oops! Didn't catch that")

# Start listening in the background
logging.info("Main        : Before the voice recognition thread")
stop_on = r.listen_in_background(mic, callback_listen, phrase_time_limit=3)

# ------------------ Run program until user ends it -----------------------
while True:
    # Perform ambient noise adjustments in a determined frequency
    if abs(time.time() - last_ambient_noise_measurement) > frequency_adjust_ambient_noise:
        logging.info("Main        : start adjusting for ambient noise in the loop")
        
        r.adjust_for_ambient_noise(source, duration=0.5)

        logging.info("Main:       : Adjusted for ambient noise in the loop")
        
        last_ambient_noise_measurement = time.time()
    else:
        time.sleep(10)

logging.info("Main        : end script")