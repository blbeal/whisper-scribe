import subprocess
import tempfile
import os
import wave
import numpy as np
import re

class SubprocessWhisper:
    def __init__(self, model_path):
        self.model_path = model_path
        # Check if main.exe exists in the extracted directory
        self.exe_path = os.path.join(os.path.dirname(__file__), 'main.exe')
        if not os.path.exists(self.exe_path):
            # Look in other common locations
            alt_path = os.path.join(os.path.dirname(__file__), 'whisper-precompiled', 'main.exe')
            if os.path.exists(alt_path):
                self.exe_path = alt_path
        
        print(f"Using whisper executable at: {self.exe_path}")
        
    def transcribe(self, audio_data):
        # Save audio data to a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Write audio data to WAV file
        with wave.open(temp_filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            # Convert float32 audio to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        try:
            # Call the whisper.cpp executable with the temp file
            cmd = [
                self.exe_path,
                '-m', self.model_path,
                '-f', temp_filename,
                '-t', '4'  # Use 4 threads
            ]
            print(f"Running command: {' '.join(cmd)}")
            
            # Run the command and capture output
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Extract transcribed text from output
            if result.returncode == 0:
                # Print the original output for debugging
                print("Original whisper.cpp output:")
                print(result.stdout)
                
                # Process all lines with timestamps
                output_lines = result.stdout.split('\n')
                transcription = ""
                
                # Process each line for timestamps
                for line in output_lines:
                    # Look for timestamp pattern
                    if '[' in line and ' --> ' in line and ']' in line:
                        # Extract text after the timestamp
                        parts = line.split(']')
                        if len(parts) > 1:
                            text = parts[1].strip()
                            # Skip blank audio markers
                            if "[BLANK_AUDIO]" in text:
                                text = text.replace("[BLANK_AUDIO]", "").strip()
                            # Only add non-empty text
                            if text:
                                transcription += text + " "
                
                # Clean up the transcription
                # Remove any remaining special tags or markers
                clean_transcription = re.sub(r'\[.*?\]', '', transcription).strip()
                
                # Print the extracted transcription for debugging
                print(f"Extracted transcription: '{clean_transcription}'")
                
                return clean_transcription
            else:
                print(f"Error running whisper.cpp: {result.stderr}")
                return f"Error: {result.stderr}"
        finally:
            # Clean up the temporary file
            try:
                os.remove(temp_filename)
            except:
                pass