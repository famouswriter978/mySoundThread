import os
import tkinter.filedialog
import tkinter.ttk

from RawRecorder import *
import pydub
from whisper_to_write import *
from threading import Thread
from datetime import datetime
from pvrecorder import PvRecorder


def load_root_config(config_file_path):
    global root_config
    root_config = configparser.ConfigParser()
    if os.path.isfile(config_file_path):
        root_config.read(config_file_path)
    else:
        cfg_file = open(config_file_path, 'w')
        root_config.add_section('Root Preferences')
        root_config.set('Root Preferences', 'recordings path', config_file_path)
        root_config.write(cfg_file)
        cfg_file.close()
    return root_config


def save_root_config(config_file_path):
    global root_config
    if os.path.isfile(config_file_path):
        cfg_file = open(config_file_path, 'w')
        root_config.write(cfg_file)
        cfg_file.close()
        print('Saved', config_file_path)
    return root_config


class myRecorder:

    def __init__(self, pwd_path, channels=1, rate=44100, frames_per_buffer=1024, format_out='mp3'):
        self.recorder = Recorder(channels=channels, rate=rate, frames_per_buffer=frames_per_buffer)
        self.file_path = None
        self.out_path = None
        self.txt_path = None
        self.pwd_path = pwd_path
        self.running = None
        self.format_out = format_out
        self.thd_num = 0
        self.thread = []

    def quit(self):
        for i in range(self.thd_num):
            self.thread[i].join()
            print('stopped thread', i)

    def start(self):
        self.file_path = os.path.join(self.pwd_path, 'test.wav')
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
            self.out_path = os.path.join(self.pwd_path, file_name)
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
script_loc = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_loc, 'root_config.ini')
root_config = load_root_config(config_path)
path = root_config['Root Preferences']['recordings path']

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
root.title('fwgWhisper')
icon_path = os.path.join(script_loc, 'fwg.png')
root.iconphoto(False, tk.PhotoImage(file=icon_path))


def select_recordings_folder():
    global path
    global folder_button
    global root_config
    path = tk.filedialog.askdirectory(title="Select a Recordings Folder")
    os.chdir(path)
    print('changed working directory to', path)
    folder_button.config(text=path)
    before_folder = root_config['Root Preferences']['recordings path']
    root_config.set('Root Preferences', 'recordings path', path)
    after_folder = root_config['Root Preferences']['recordings path']
    save_root_config(config_path)
    print('Changed recordings folder from\n', before_folder, '\nto\n', after_folder)


folder_label = tk.Label(root, text='Recordings path')
folder_label.pack()
folder_button = tk.Button(root, text=path, command=select_recordings_folder)
folder_button.pack(ipadx=5, pady=5)
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
