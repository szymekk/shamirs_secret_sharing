# Shamir's secret sharing

A Python implementation of [Shamir's secret sharing scheme](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing).
The scheme allows splitting a secret message into N fragments.
Any K fragments can be combined to retrieve the original secret whereas any number of fragments less than K does not reveal any information about original message.
The implementation of the splitting and combining algorithms is exposed through a simple graphical application built with PyQt5.

## Running

Fetch the dependencies using pip.
```
pip install -r requirements.txt
```
Optionally run tests to ensure the core sharing and splitting algorithms work correctly
```
python -m test_shamir
```
Run the GUI application directly with
```
python -m secret_sharing_gui
```
Optionally generate a standalone executable with pyinstaller
```
pyinstaller secret_sharing_gui.py --onefile --windowed
```
and run it with
```
./dist/secret_sharing_gui
```
or (on Windows)
```
.\dist\secret_sharing_gui.exe
```

The generated executable is self-contained, i.e. contains copies of the script, the CPython interpreter, and all other dependencies.
This makes it somewhat big but allows running the application on a computer without the required dependencies (including the Python interpreter).
