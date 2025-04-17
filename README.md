# Whisper.cpp Desktop Transcription Tool

A desktop transcription application that lets you transcribe speech to text in any text field using a hotkey. The application runs in the system tray and uses a hotkey (Alt+period) to activate recording, transcribes the speech using whisper.cpp, and then types the transcribed text at the cursor position.

## Features

- **System Tray Application:** Runs quietly in the background with minimal UI
- **Hotkey Activation:** Press Alt+period to start and stop recording
- **Real-time Audio Recording:** Records from your default microphone
- **Speech Recognition:** Uses whisper.cpp for accurate transcription
- **Text Insertion:** Automatically types the transcribed text at your cursor position
- **Notifications:** Provides feedback through system notifications

# Whisper.cpp Desktop Transcription Tool

A desktop application that allows users to transcribe speech to text in any text field using a hotkey (Alt+period). The application runs in the system tray and transcribes speech using whisper.cpp.

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