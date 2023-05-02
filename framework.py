import tkinter as tk
from RawRecorder import *
import pydub

# --- functions ---


def start():
    global running
    global file_name

    if running is not None:
        print('already running')
    else:
        running = recorder.open(file_name)
        running.start_recording()
        print('started recording')


def stop():
    global running
    global file_name
    global out_format

    if running is not None:
        running.stop_recording()
        running.close()
        running = None
        print('stopped recording')
        pydub.AudioSegment.from_wav(file_name).export(file_name + '.' + out_format, out_format=out_format)
    else:
        print('not running')


# --- main ---
recorder = Recorder(channels=1, rate=44100, frames_per_buffer=1024)
running = None
file_name = './framework.wav'
out_format = 'mp3'

root = tk.Tk()

button_recorder = tk.Button(root, text='Start', command=start)
button_recorder.pack()

button_stop = tk.Button(root, text='Stop', command=stop)
button_stop.pack()

root.mainloop()
