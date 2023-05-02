# mySoundThread

# There are instructions for each platform
Before going there, download the source code now because it's right at the top of this page:  click on the green box titled '<> Code' and 'Download ZIP' file.   Of course, you should skip this step is planning to use the 'GitHub Desktop App'.  Coming back here and locating the download will be difficult later and easy now.   The installation will explain what to do with the '.zip' file.

[macOS](doc/FAQ_macos.md)

[Windows](doc/FAQ_windows.md)

[Linux](doc/FAQ_linux.md)

# There are special developer instructions if desired
[Special Developer Instructions](doc/DEVELOPER.md)

## Approach

![Approach](doc/Whisper-FWG.png)

We're wrapping an existing tool to make it easy for non-tech people to use.  After installation, only mouse clicks are required to enjoy using it.

The existing tool, 'whisper,' requires installation of python.   So knowing that python must be installed, this tool comes as a python package.   Download this package, install python3.10 and higher, run pip as instructed herein, and it should work from the command line.   You can finish with a flourish by making a shortcut to the command line command.

Supposedly 'whisper' works on 3.6 - 3.9 but these wrapper scripts have problems with those, in the area of the 'tkinter' functions.

[or online](https://github.com/openai/whisper)
