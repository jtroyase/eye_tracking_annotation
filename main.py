import microphone
import image
import gaze

# Create video recorder thread
video_thread = image.VideoRecorder()
video_thread.start()

# Create eye tracker thread
eye_thread = gaze.EyeTracker()
eye_thread.start()

# Create microphone recorder thread
audio_thread = microphone.Microphone()
audio_thread.start()

# Wait for all threads to finish
# video_thread.join()
# eye_thread.join()
# audio_thread.join()