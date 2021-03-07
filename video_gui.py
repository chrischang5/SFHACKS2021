import threading
import tkinter
from tkinter import Grid, simpledialog
import cv2
import PIL.Image, PIL.ImageTk
import time
import datetime
from input_gui import MaxTimeWindow
from cloud_vision import cloud_vision_helpers
import os

counter = 0
running = False


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
        # self.btn_max_time = tkinter.Button(window, text="Set max time limit", width=30, command=self.set_max_timer_window )
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
            i += 1

    def snapshot(self):
        # Get a frame from the video source
        self.counting += 1
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite(f"frame-{self.counting}.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

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
        self.btn_start['state'] = 'disabled'
        self.btn_stop['state'] = 'normal'
        threading.Timer(10, self.snapshot).start()
        # self.snapshot()


    # Stop function of the stopwatch
    def stop(self):
        global running
        self.btn_start['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'
        running = False
        # self.stop_snapshot()
        threading.Timer(10, self.snapshot).cancel()
        self.cv_function()


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
