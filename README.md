# Whisper.cpp Desktop Transcription Tool

A desktop application that allows users to transcribe speech to text in any text field using a hotkey (Alt+period). The application runs in the system tray and transcribes speech using whisper.cpp offline.

## Features
- System tray application with hotkey activation (Alt+period)
- Real-time audio recording
- Integration with whisper.cpp for speech recognition
- Text insertion at cursor position

## Requirements
- Python 3.10+
- PySide6
- numpy
- sounddevice
- pyautogui
- pynput
- whisper.cpp executable (main.exe)
- whisper model file (ggml-base.en.bin)

## Setup Instructions
1. Clone this repository
2. Install required Python packages: `pip install PySide6 numpy sounddevice pyautogui pynput`
3. Download whisper.cpp executable and place it in the project root
4. Download a whisper model file and place it in `whisper.cpp/models/`
5. Run the application: `python main.py`

## Usage
- Press Alt+period to start recording
- Speak into your microphone
- Press Alt+period again to stop recording and transcribe
- The transcribed text will be typed at your cursor position