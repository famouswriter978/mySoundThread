import os
import tkinter as tk
from RawRecorder import *
import pydub
from whisper_to_write import *
from threading import Thread

class myRecorder:

    def __init__(self, cwd_path, channels=1, rate=44100, frames_per_buffer=1024, format_out='mp3'):
        self.recorder = Recorder(channels=channels, rate=rate, frames_per_buffer=frames_per_buffer)
        self.file_path = None
        self.out_path = None
        self.txt_path = None
        self.cwd_path = cwd_path
        self.running = None
        self.format_out = format_out
        self.thd_num = 0
        self.thread = []

    def quit(self):
        for i in range(self.thd_num):
            self.thread[i].join()
            print('stopped thread', i)

    def start(self):

        self.file_path = os.path.join(self.cwd_path, 'test.wav')
        self.out_path = self.file_path.replace('wav', 'mp3')
        self.txt_path = self.file_path.replace('wav', 'txt')
        if self.running is not None:
            print('already running')
        else:
            self.running = self.recorder.open(self.file_path)
            self.running.start_recording()
            print('started recording', self.file_path)

    def stop(self):
        if self.running is not None:
            self.running.stop_recording()
            self.running.close()
            self.running = None
            print('Stopped recording; output in ', self.file_path)
            pydub.AudioSegment.from_wav(self.file_path).export(self.out_path, format=self.format_out)
            # try:
            os.remove(self.file_path)
            print('Converted', self.file_path, 'to', self.out_path)
            # whisper_to_write(filepaths=(self.out_path,), fast=True)
            args = ('', 'cpu', self.out_path, 'False', 'True')
            # whisper_thd = Thread(target=whisper_to_write, args=args)
            # whisper_thd.start()
            # whisper_thd.join()
            self.thread.append(Thread(target=whisper_to_write, args=args))
            self.thread[self.thd_num].start()
            self.thd_num += 1
            print('started thread', self.thd_num)
            # except OSError:
            #     print('Conversion from', self.file_path, 'to', self.out_path, 'failed')
            #     pass
        else:
            print('not running')


def start():
    recorder.start()


def stop():
    recorder.stop()


def quitting():
    recorder.quit()


# --- main ---

# Configuration for entire folder selection read with filepaths
cwd_path = os.getcwd()
recorder = myRecorder(cwd_path)

root = tk.Tk()

button_recorder = tk.Button(root, text='Start', command=start)
button_recorder.pack()

button_stop = tk.Button(root, text='Pause', command=stop)
button_stop.pack()

button_quit = tk.Button(root, text='Quit', command=quitting)
button_quit.pack()

root.mainloop()
