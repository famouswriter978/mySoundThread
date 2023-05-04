import os
import tkinter as tk
from RawRecorder import *
import pydub
from whisper_to_write import *
from threading import Thread
from datetime import datetime
from pvrecorder import PvRecorder


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
        self.txt_path = self.file_path.replace('wav', 'txt')
        if self.running is not None:
            print('already recording')
        else:
            self.running = self.recorder.open(self.file_path)
            self.running.start_recording()
            print('started recording', self.file_path)

    def transcribe(self):
        try:
            args = ('', 'cpu', None, 'True', 'False')  # default args to force select/convert
            self.thread.append(Thread(target=whisper_to_write, args=args))
            self.thread[self.thd_num].start()
            self.thd_num += 1
            print('started thread', self.thd_num)
        except OSError:
            print('Transcription failed')
            pass

    def stop(self):
        if self.running is not None:
            file_name = 'speak_write' + str(datetime.now()).replace(':', '-').replace('.', '-') + '.mp3'
            self.out_path = os.path.join(self.cwd_path, file_name)
            self.running.stop_recording()
            self.running.close()
            self.running = None
            print('Stopped recording; audio output in ', self.file_path)
            pydub.AudioSegment.from_wav(self.file_path).export(self.out_path, format=self.format_out)
            try:
                os.remove(self.file_path)
                print('Converted', self.file_path, 'to', self.out_path)
                # whisper_to_write(filepaths=(self.out_path,), fast=True)
                args = ('', 'cpu', self.out_path, 'False', 'True')
                self.thread.append(Thread(target=whisper_to_write, args=args))
                self.thread[self.thd_num].start()
                self.thd_num += 1
                print('started thread', self.thd_num)
            except OSError:
                print('Conversion from', self.file_path, 'to', self.out_path, 'failed')
                pass
        else:
            print('not running')


def start():
    recorder.start()


def stop():
    recorder.stop()


def transcribe():
    recorder.transcribe()


def quitting():
    recorder.quit()
    exit(0)


# --- main ---
# Configuration for entire folder selection read with filepaths
cwd_path = os.getcwd()
recorder = myRecorder(cwd_path)

# Get/check microphone
mic_avail = True
try:
    audio_devices = PvRecorder.get_audio_devices()
    for index, device in enumerate(audio_devices):
        print(f"[{index}] {device}")
    pa = pyaudio.PyAudio()
    default = pa.get_default_input_device_info()  # raises IOError
    print('using', default['name'])
except IOError:
    print(Colors.fg.red, 'Default microphone not found.  Capability limited', Colors.reset)
    mic_avail = False

# Define frame
root = tk.Tk()
if mic_avail:
    button_recorder = tk.Button(root, text='Dictate', command=start)
    button_recorder.pack()

    button_stop = tk.Button(root, text='Stop', command=stop)
    button_stop.pack()
else:
    button_recorder = tk.Button(root, text='NO MIC')
    button_recorder.pack()
button_recorder = tk.Button(root, text='Transcribe a File', command=transcribe)
button_recorder.pack()
button_quit = tk.Button(root, text='Quit', command=quitting)
button_quit.pack()

# Begin
root.mainloop()
