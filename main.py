import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QThread, Signal
from pynput import keyboard
import numpy as np
import sounddevice as sd
import pyautogui
import time
from whisper_wrapper import Whisper
import traceback
from subprocess_whisper import SubprocessWhisper

class AudioRecorder(QThread):
    """Thread for recording audio without blocking the main application"""
    finished = Signal(np.ndarray)
    
    def __init__(self, sample_rate=16000):
        super().__init__()
        self.sample_rate = sample_rate  # 16kHz is good for speech recognition
        self.recording = True
        self.audio_data = []
        
    def run(self):
        """Record audio until stopped"""
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
                
        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback):
            while self.recording:
                self.msleep(10)  # Sleep to avoid high CPU usage
                
        # Process recorded audio
        if self.audio_data:
            audio = np.concatenate(self.audio_data, axis=0).flatten()
            self.finished.emit(audio)
            
    def stop(self):
        """Stop recording"""
        self.recording = False

class WhisperApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        # Prevent app from closing when all windows are closed
        self.setQuitOnLastWindowClosed(False)
        
        # Initialize recorder
        self.recorder = None
        
        # Set up system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon("microphone.png"))
        # Initialize whisper model
        model_path = os.path.join(os.path.dirname(__file__), 'whisper.cpp', 'models', 'ggml-base.en.bin')
        try:
            self.whisper = SubprocessWhisper(model_path)
            print(f"Whisper model loaded from {model_path}")
        except Exception as e:
            print(f"Error loading whisper model: {e}")
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Traceback: {traceback_str}")
            self.whisper = None
        
        self.tray_icon.setToolTip("Whisper Transcriber")   

        # Create tray menu
        menu = QMenu()
        
        # Add a status action to the menu
        self.status_action = QAction("Ready", self)
        self.status_action.setEnabled(False)  # Not clickable
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Add a quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        
        # Set menu on tray icon
        self.tray_icon.setContextMenu(menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Initialize recording state
        self.is_recording = False
        
        # Initialize alt key state
        self.alt_pressed = False

        # Start listening for hotkey
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        self.listener.start()
        print("Keyboard listener started successfully")
        
        # Show startup notification
        self.tray_icon.showMessage(
            "Whisper Transcriber", 
            "Press Alt+Period to start recording", 
            QSystemTrayIcon.Information, 
            3000
        )
    
    def on_press(self, key):
        """Handle key press events"""
        print(f"Key pressed: {key}")
        
        try:
            # Track if any Alt key is pressed (including Alt Graph)
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr:
                self.alt_pressed = True
                print("Alt pressed")
            
            # Check if it's a period key while Alt is held
            elif hasattr(key, 'char') and key.char == '.':
                print("Period key detected")
                # Only trigger the action if Alt is pressed
                if self.alt_pressed:
                    print("Alt+. hotkey detected!")
                    self.toggle_recording()
                else:
                    print("Period pressed without Alt - ignoring")
        except AttributeError as e:
            print(f"AttributeError: {e}")
            pass

    def on_release(self, key):
        """Handle key release events"""
        try:
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr:
                self.alt_pressed = False
                print("Alt released")
        except AttributeError:
            pass
        
    def toggle_recording(self):
        """Toggle recording state when hotkey is pressed"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.status_action.setText("Recording...")
            self.tray_icon.setToolTip("Recording...")
            
            # Start recorder thread
            self.recorder = AudioRecorder()
            self.recorder.finished.connect(self.handle_audio)
            self.recorder.start()
            
            # Show notification
            self.tray_icon.showMessage(
                "Whisper Transcriber", 
                "Recording started", 
                QSystemTrayIcon.Information, 
                1000
            )
        else:
            # Immediately update UI to show we're stopping
            self.is_recording = False
            self.status_action.setText("Processing...")
            self.tray_icon.setToolTip("Processing...")
            
            # Show immediate notification
            self.tray_icon.showMessage(
                "Whisper Transcriber", 
                "Recording stopped - processing audio...", 
                QSystemTrayIcon.Information, 
                1000
            )
            
            # Then stop the recorder
            if self.recorder:
                self.recorder.stop()
    
    def handle_audio(self, audio):
        """Process recorded audio and insert transcribed text at cursor position"""
        if not self.whisper:
            self.tray_icon.showMessage(
                "Error",
                "Whisper model not loaded",
                QSystemTrayIcon.Critical,
                3000
            )
            self.status_action.setText("Ready")
            self.tray_icon.setToolTip("Whisper Transcriber")
            return
        
        try:
            # Update status
            self.status_action.setText("Transcribing...")
            self.tray_icon.setToolTip("Transcribing...")
            
            # Begin transcription
            text = self.whisper.transcribe(audio)
            
            # Insert text at cursor position
            if text:
                # Add a small delay to ensure the application is ready
                time.sleep(0.5)
                
                # Type the transcribed text
                pyautogui.write(text)
                
                # Show notification
                self.tray_icon.showMessage(
                    "Transcription Complete",
                    f"Inserted: {text[:30]}{'...' if len(text) > 30 else ''}",
                    QSystemTrayIcon.Information,
                    2000
                )
            else:
                self.tray_icon.showMessage(
                    "No Speech Detected",
                    "Try speaking more clearly or adjusting your microphone",
                    QSystemTrayIcon.Information,
                    2000
                    )
        except Exception as e:
            self.tray_icon.showMessage(
                "Error",
                f"Transcription failed: {e}",
                QSystemTrayIcon.Critical,
                3000
            )
            print(f"Error during transcription: {e}")
        
        # Reset status
        self.status_action.setText("Ready")
        self.tray_icon.setToolTip("Whisper Transcriber")

if __name__ == "__main__":
    app = WhisperApp(sys.argv)
    sys.exit(app.exec())