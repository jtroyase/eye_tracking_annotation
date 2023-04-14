import time
import threading
import numpy as np
import ndsi  # Main requirement
import logging
import speech_recognition as sr
from collections import deque


class EyeTracker(threading.Thread):
    def __init__(self):
        super().__init__()
        # Initialize eye tracking glasses here

        self.SENSOR_TYPES = ["gaze"]
        self.SENSORS = {}

        # Start auto-discovery of Pupil Invisible Companion devices
        self.network = ndsi.Network(
            formats={ndsi.DataFormat.V4}, callbacks=(self.on_network_event,))
        self.network.start()
        logging.info("gaze_       : Network started")

        self.output = []
        self.is_running = False

        self.frequency = 1 # Set the frequency of data gaze to one second
        self.last_measurement = float('inf')

    def obtain_gaze(self):
        '''
        This method is runned to obtain data gaze.
        '''
        logging.info('gaze_       : in obtain gaze')
        gaze = (0,0)
        
        try:
            # Event loop, runs until interrupted
            while self.network.running:
                
                # Check if data needs to be retrieved
                if self.is_running == True:
                    if abs(time.time() - self.last_measurement) > self.frequency: #Check frequency of data to be retrieved

                        # Check for recently connected/disconnected devices
                        if self.network.has_events:
                            self.network.handle_event()

                        # Iterate over all connected devices
                        for sensor in self.SENSORS.values():

                            # We only consider gaze and video
                            if sensor.type not in self.SENSOR_TYPES:
                                continue

                            # Fetch recent sensor configuration changes,
                            # required for pyndsi internals
                            while sensor.has_notifications:
                                sensor.handle_notification()

                            # Fetch recent gaze data
                            data_deque = deque(sensor.fetch_data(), maxlen=1)
                            if data_deque:
                                last_data = data_deque.pop()
                            
                                if sensor.name == "Gaze":
                                    # Draw gaze overlay onto world video frame
                                    gaze = (int(last_data[0]), int(last_data[1]))
                                    logging.info(gaze)
                                    self.last_measurement = time.time()

                else:
                    break
                
        # Catch interruption and disconnect gracefully
        except (KeyboardInterrupt, SystemExit):
            print(self.output)
            self.network.stop()

    def on_network_event(self, network, event):
        # Handle gaze sensor attachment
        if event["subject"] == "attach" and event["sensor_type"] in self.SENSOR_TYPES:
            # Create new sensor, start data streaming,
            # and request current configuration
            sensor = self.network.sensor(event["sensor_uuid"])
            sensor.set_control_value("streaming", True)
            sensor.refresh_controls()

            # Save sensor s.t. we can fetch data from it in main()
            self.SENSORS[event["sensor_uuid"]] = sensor
            #print(f"Added sensor {sensor}...")

        # Handle gaze sensor detachment
        if event["subject"] == "detach" and event["sensor_uuid"] in self.SENSORS:
            # Known sensor has disconnected, remove from list
            self.SENSORS[event["sensor_uuid"]].unlink()
            del self.SENSORS[event["sensor_uuid"]]
            print(f"Removed sensor {event['sensor_uuid']}...")

    def stop(self):
        logging.info('gaze_       : stopping gaze')
        self.is_running = False
