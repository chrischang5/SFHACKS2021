import threading
import pyaudio
import wave
from SpeechRecognize import Speech
import tkinter
from tkinter import Grid, simpledialog
import cv2
import PIL.Image, PIL.ImageTk
import time
import datetime
#from input_gui import MaxTimeWindow
from cloud_vision import cloud_vision_helpers
import os

counter = 0
running = False

class AudioRecorder:

    # Audio class based on pyAudio and Wave
    def __init__(self):

        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio2.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.audio_frames = []

    # Audio starts being recorded
    def record(self):

        self.stream.start_stream()
        while self.open:
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if not self.open:
                break

    # Finishes the audio recording therefore the thread too
    def stop(self):

        if self.open:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()

        pass

    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.counting = 0

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        label = tkinter.Label(window, text="Welcome!", fg="black", font="Verdana 30 bold")
        label.pack()

        # Button that lets the user take a snapshot
        # self.btn_snapshot = tkinter.Button(window, text="Snapshot", width=30, command=self.snapshot)
        # self.btn_snapshot.pack(side=tkinter.LEFT)
        # self.btn_snapshot.grid(row=0,column=0,sticky="NSEW")

        # Button for start
        self.btn_start = tkinter.Button(window, text="Start", width=30, command=lambda: self.start(label))
        self.btn_start.pack(side=tkinter.LEFT)
        # self.btn_start.grid(row=0, column=0, sticky="NSEW")

        # Button for stop
        self.btn_stop = tkinter.Button(window, text="Stop", width=30, fg="red", command=self.stop)
        self.btn_stop.pack(side=tkinter.LEFT)
        # self.btn_stop.grid(row=0, column=0, sticky="NSEW")

        # Button for Input
        # self.btn_max_time = tkinter.Button(window, text="Set max time limit", width=30,
        # command=self.set_max_timer_window )
        # self.btn_max_time.pack(side=tkinter.LEFT)
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def cv_function(self):
        localpath = os.getcwd()
        c = self.counting
        i = 1
        while (i <= c):
            cloud_vision_helpers.detect_faces(str(localpath) + r"\frame-" + str(i) + ".jpg")
            os.remove(str(localpath) + r"\frame-" + str(i) + ".jpg")
            i += 1

    def speechtotext(self):
        localpath = os.getcwd()
        Speech.transform()
        Speech.transcribe_file(str(localpath) + r"\temp_audio3.flac")

    def snapshot(self):
        # Get a frame from the video source
        self.counting += 1
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite(f"frame-{self.counting}.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        #threading.Timer(10, self.snapshot).start()

    def stop_snapshot(self):
        threading.Timer(10, self.snapshot).cancel()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)

    def set_max_timer_window(self):
        self._popup_win = tkinter.Toplevel()
        self._popup = MaxTimeWindow(self._popup_win, self._close_student_cb)

        # max_time_window = simpledialog.askinteger(title="Test",
        #                                   prompt="Maximum Time")
        # max_time_window = tkinter.Toplevel(self.window)
        # max_time_window.geometry("300x200")
        # tkinter.Label(max_time_window, text="Maximum Time").pack()

    def _close_student_cb(self):
        """ Close Add Student Popup """
        self._popup_win.destroy()

    # https://www.geeksforgeeks.org/create-stopwatch-using-python/
    def counter_label(self, label):
        def count():
            if running:
                global counter
                # To manage the intial delay.
                if counter == 0:
                    display = "Starting..."
                else:

                    tt = datetime.datetime.fromtimestamp(counter)
                    string = tt.strftime("%M:%S")
                    display = string

                label['text'] = display  # Or label.config(text=display)

                label.after(1000, count)
                counter += 1

        # Triggering the start of the counter.
        count()

    def start(self, label):
        global running
        running = True
        self.counter_label(label)
        self.start_audio_recording()
        self.btn_start['state'] = 'disabled'
        self.btn_stop['state'] = 'normal'
        threading.Timer(10, self.snapshot).start()
        #self.snapshot()


    # Stop function of the stopwatch
    def stop(self):
        global running
        self.btn_start['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'
        self.stop_AVrecording()
        running = False
        # self.stop_snapshot()
        threading.Timer(10, self.snapshot).cancel()
        self.cv_function()
        self.speechtotext()

    def file_manager(filename):
        local_path = os.getcwd()

        if os.path.exists(str(local_path) + "/temp_audio2.wav"):
            os.remove(str(local_path) + "/temp_audio2.wav")

        if os.path.exists(str(local_path) + "/" + filename + ".avi"):
            os.remove(str(local_path) + "/" + filename + ".avi")

    def start_audio_recording(filename):
        global audio_thread

        audio_thread = AudioRecorder()
        audio_thread.start()

        return filename

    def stop_AVrecording(filename):
        audio_thread.stop()
        # frame_counts = video_thread.frame_counts
        # elapsed_time = time.time() - video_thread.start_time
        # recorded_fps = frame_counts / elapsed_time
        # print("total frames " + str(frame_counts))
        # print("elapsed time " + str(elapsed_time))
        # print("recorded fps " + str(recorded_fps))
        # video_thread.stop()

        # Makes sure the threads have finished
        while threading.active_count() > 1:
            time.sleep(1)

        # Merging audio and video signal

        # if abs(recorded_fps - 6) >= 0.01:  # If the fps rate was higher/lower than expected, re-encode it to the expected
        #
        #     print("Re-encoding")
        #     cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
        #     subprocess.call(cmd, shell=True)
        #
        #     print("Muxing")
        #     cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
        #     subprocess.call(cmd, shell=True)
        #
        # else:
        #
        #     print("Normal recording\nMuxing")
        #     cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
        #     subprocess.call(cmd, shell=True)
        #
        #     print("..")


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self, ret=None):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return ret, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# Create a window and pass it to the Application object
App(tkinter.Tk(), "AUDIENCE")
