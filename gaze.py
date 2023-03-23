import time
import threading
import numpy as np
import ndsi  # Main requirement


class EyeTracker(threading.Thread):
    def __init__(self):
        super().__init__()
        # Initialize eye tracking glasses here
        self.is_running = True

        self.SENSOR_TYPES = ["gaze"]
        self.SENSORS = {}

        # Start auto-discovery of Pupil Invisible Companion devices
        self.network = ndsi.Network(
            formats={ndsi.DataFormat.V4}, callbacks=(self.on_network_event,))
        self.network.start()

        self.output = []
        self.obtain_gaze()

    def obtain_gaze(self):
        gaze = (0,0)

        try:
            # Event loop, runs until interrupted
            while self.network.running:
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
                    for data in sensor.fetch_data():
                        if data is None:
                            continue

                        if sensor.name == "Gaze":
                            # Draw gaze overlay onto world video frame
                            gaze = (int(data[0]), int(data[1]))
                            self.output.append((time.time(), gaze))
            
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