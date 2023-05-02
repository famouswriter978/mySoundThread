import tkinter as tk
from RawRecorder import *
import pydub


class myRecorder:

    def __init__(self, file_path, channels=1, rate=44100, frames_per_buffer=1024, format_out='mp3'):
        self.recorder = Recorder(channels=channels, rate=rate, frames_per_buffer=frames_per_buffer)
        self.file_path = file_path
        self.running = None
        self.format_out = format_out

    def start(self):

        if self.running is not None:
            print('already running')
        else:
            self.running = self.recorder.open(self.file_path + '.wav')
            self.running.start_recording()
            print('started recording', self.file_path)

    def stop(self):
        if self.running is not None:
            self.running.stop_recording()
            self.running.close()
            self.running = None
            print('stopped recording')
            pydub.AudioSegment.from_wav(self.file_path + '.wav').export((self.file_path + '.' + self.format_out),
                                                                        format=self.format_out)
        else:
            print('not running')


def start():
    recorder.start()


def stop():
    recorder.stop()


# --- main ---
recorder = myRecorder('./framework')

root = tk.Tk()

button_recorder = tk.Button(root, text='Start', command=start)
button_recorder.pack()

button_stop = tk.Button(root, text='Stop', command=stop)
button_stop.pack()

root.mainloop()
