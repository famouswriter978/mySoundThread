#  Graphical interface to whisper:  dictate, read file, transcribe
#  Run in PyCharm
#     or
#  'python3 speak_write.py'
#
#  2023-May-04  Dave Gutz   Create
# Copyright (C) 2023 Dave Gutz
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# See http://www.fsf.org/licensing/licenses/lgpl.txt for full license text.

import tkinter.filedialog
import tkinter.ttk
from RawRecorder import *
import pydub
from whisper_to_write import *
from threading import Thread
from datetime import datetime
from pvrecorder import PvRecorder


# Executive class to control the global variables
class ExRoot:
    def __init__(self):
        self.script_loc = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_loc, 'root_config.ini')
        self.root_config = None
        self.path = None
        self.root_config = None
        self.load_root_config(self.config_path)
        self.folder_button = None

    def select_recordings_folder(self):
        self.path = tk.filedialog.askdirectory(title="Select a Recordings Folder")
        os.chdir(self.path)
        print('changed working directory to', self.path)
        self.folder_button.config(text=self.path)
        before_folder = self.root_config['Root Preferences']['recordings path']
        self.root_config.set('Root Preferences', 'recordings path', self.path)
        after_folder = self.root_config['Root Preferences']['recordings path']
        self.save_root_config(self.config_path)
        print('Changed recordings folder from\n', before_folder, '\nto\n', after_folder)

    def load_root_config(self, config_file_path):
        self.root_config = configparser.ConfigParser()
        if os.path.isfile(config_file_path):
            self.root_config.read(config_file_path)
        else:
            cfg_file = open(config_file_path, 'w')
            self.root_config.add_section('Root Preferences')
            self.root_config.set('Root Preferences', 'recordings path', config_file_path)
            self.root_config.write(cfg_file)
            cfg_file.close()
        self.path = self.root_config['Root Preferences']['recordings path']
        print('Recordings folder is', self.path)
        return self.root_config

    def save_root_config(self, config_path_):
        if os.path.isfile(config_path_):
            cfg_file = open(config_path_, 'w')
            self.root_config.write(cfg_file)
            cfg_file.close()
            print('Saved', config_path_)
        return self.root_config


# Wrap thread class so can extract resulting filename
class CustomThread(Thread):
    def __init__(self, audio_path, waiting, silent, recordings_folder):
        Thread.__init__(self)
        self.waiting = waiting
        self.silent = silent
        self.audio_path = audio_path
        self.result_path = None
        self.recordings_folder = recordings_folder

    def run(self):
        self.result_path = whisper_to_write(model='', device='cpu', file_in=self.audio_path,
                                            waiting=self.waiting, silent=self.silent)
        if self.result_path is not None:
            print('Results displayed automatically at quit')


class myRecorder:

    def __init__(self, rec_path, channels=1, rate=44100, frames_per_buffer=1024, format_out='mp3'):
        self.recorder = Recorder(channels=channels, rate=rate, frames_per_buffer=frames_per_buffer)
        self.file_path = None
        self.audio_path = None
        self.txt_path = None
        self.rec_path = rec_path
        self.running = None
        self.format_out = format_out
        self.thd_num = -1
        self.thread = []
        self.result_file = None

    def quit(self):
        for i in range(self.thd_num+1):
            self.thread[i].join()
            if self.thread[i].result_path is not None:
                display_result(self.thread[i].result_path, platform, False)
                print('stopped thread', i, ': result in', self.thread[i].result_path)
            else:
                print('stopped thread', i, ': result was screened')

    def start(self):
        self.file_path = os.path.join(self.rec_path, 'test.wav')
        self.txt_path = self.file_path.replace('wav', 'txt')
        if self.running is not None:
            print('already recording')
        else:
            self.running = self.recorder.open(self.file_path)
            self.running.start_recording()
            print('started recording', self.file_path)

    def transcribe(self):
        try:
            self.thread.append(CustomThread(None, False, True, self.rec_path))
            self.thd_num += 1
            print('starting thread', self.thd_num, end='...')
            self.thread[self.thd_num].start()
        except OSError:
            print('Transcription failed')
            pass

    def stop(self):
        if self.running is not None:
            file_name = 'speak-write' + str(datetime.now()).replace(':', '-').replace('.', '-') + '.mp3'
            self.audio_path = os.path.join(self.rec_path, file_name)
            self.running.stop_recording()
            self.running.close()
            self.running = None
            print('Stopped recording; audio output in ', self.file_path)
            pydub.AudioSegment.from_wav(self.file_path).export(self.audio_path, format=self.format_out)
            try:
                os.remove(self.file_path)
                print('Converted', self.file_path, 'to', self.audio_path)
                self.thread.append(CustomThread(self.audio_path, False, True, self.rec_path))
                self.thd_num += 1
                print('starting thread', self.thd_num, end='...')
                self.thread[self.thd_num].start()
            except OSError:
                print('Conversion from', self.file_path, 'to', self.audio_path, 'failed')
                pass
        else:
            print('recorder was not running')


def start():
    recorder.start()


def stop():
    recorder.stop()


def select_recordings_folder():
    ex_root.select_recordings_folder()


def transcribe():
    recorder.transcribe()


def quitting():
    recorder.stop()
    recorder.quit()
    exit(0)


# --- main ---
# Configuration for entire folder selection read with filepaths
cwd_path = os.getcwd()
ex_root = ExRoot()
recorder = myRecorder(ex_root.path)

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
root.geometry('300x200')
root.title('openAI whisper')
icon_path = os.path.join(ex_root.script_loc, 'fwg.png')
root.iconphoto(False, tk.PhotoImage(file=icon_path))
folder_label = tk.Label(root, text='Recordings path')
folder_label.pack()
ex_root.folder_button = tk.Button(root, text=ex_root.path, command=select_recordings_folder)
ex_root.folder_button.pack(ipadx=5, pady=5)
separator0 = tk.ttk.Separator(root, orient='horizontal')
separator0.pack(fill='x')

if mic_avail:
    button_recorder = tk.Button(root, text='Dictate', command=start)
    button_recorder.pack()

    button_stop = tk.Button(root, text='Stop', command=stop)
    button_stop.pack()
else:
    button_recorder = tk.Button(root, text='NO MIC')
    button_recorder.pack()

separator1 = tk.ttk.Separator(root, orient='horizontal')
separator1.pack(fill='x')
button_recorder = tk.Button(root, text='Transcribe a File', command=transcribe)
button_recorder.pack(ipadx=5, pady=5)
separator2 = tk.ttk.Separator(root, orient='horizontal')
separator2.pack(fill='x')
button_quit = tk.Button(root, text='Quit', command=quitting)
button_quit.pack(ipadx=5, pady=5)

# Begin
root.mainloop()
