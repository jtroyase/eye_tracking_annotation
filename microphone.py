import speech_recognition as sr
import time
import threading

class Microphone(threading.Thread):
    def __init__(self):
        super().__init__()
        
        self.is_running = True
        
        self.wake = "activate"
        print("Start")

        self.output = []

        self.init()

    def init(self):
        # Create recognizer and microphone instance
        r = sr.Recognizer()
        mic = sr.Microphone()

        # Adjust for ambient noise
        print('Adjusting ambient noise...')
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
        print('done')

        # Adjust for pause
        #r.pause_threshold = 0.5

        timer = time.time()
        while self.is_running:
            #print("Listening")
            # Adjust for ambient noise every 5 seconds
            time_now = time.time()
            if time_now - timer > 5:
                print('Adjusting ambient noise...')
                with mic as source:
                    r.adjust_for_ambient_noise(source)
                timer = time.time()
                print('done')

            text = self.get_audio(r, mic)

            if text.count(self.wake) > 0:
                self.output.append((time.time(), self.wake))
                print('Got it!')


    def get_audio(self, r, mic):
        '''
        Listens to the microphone and recognizes
        :param r: instance of the recognizer
        :param mic: instance of the microphone
        :return said.lower(): Recognized speech-to-text
        '''

        with mic as source:
            said = ""
            audio = r.listen(source)
    
        try:
            said = r.recognize_whisper(audio, model='tiny', language="english", translate=False)
            print(said)
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Whisper")

        return said.lower()