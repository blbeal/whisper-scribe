import os
import numpy as np
import ctypes
from ctypes import c_int, c_float, c_char_p, c_bool, POINTER, Structure, byref

# Print current directory for debugging
print(f"Current directory: {os.path.dirname(__file__)}")

# Look for the DLL in the project root folder ONLY
_lib_path = os.path.join(os.path.dirname(__file__), 'whisper.dll')
print(f"Looking for whisper.dll at: {_lib_path}")

if not os.path.exists(_lib_path):
    print(f"Error: whisper.dll not found at {_lib_path}")
    print("Please download the DLL file to your project directory.")
    raise RuntimeError(f"Whisper library not found at {_lib_path}")

# Load the library and print all available functions
try:
    print(f"Loading whisper.dll from: {_lib_path}")
    _lib = ctypes.CDLL(_lib_path)
    print("Successfully loaded whisper.dll")
    
    # Try to list available functions - this may not work on all systems
    try:
        print("Available functions in the DLL:")
        for name in dir(_lib):
            if not name.startswith('_'):
                print(f"  {name}")
    except Exception as e:
        print(f"Could not list functions: {e}")
        
except Exception as e:
    print(f"Failed to load whisper.dll: {e}")
    raise

# Define whisper_context structure (opaque pointer)
class whisper_context(Structure):
    pass

# Simple whisper_full_params structure with minimum required fields
class whisper_full_params(Structure):
    _fields_ = [
        ("strategy", c_int),
        ("n_threads", c_int),
        ("n_max_text_ctx", c_int),
        ("offset_ms", c_int),
        ("duration_ms", c_int),
        ("translate", c_bool),
        ("no_context", c_bool),
        ("single_segment", c_bool),
        ("print_special", c_bool),
        ("print_progress", c_bool),
        ("print_realtime", c_bool),
        ("print_timestamps", c_bool),
    ]

# Create a simple class to handle execution
class DummyWhisper:
    """A dummy implementation that simulates transcription for testing"""
    def __init__(self, model_path):
        print(f"DummyWhisper: Pretending to load model from {model_path}")
    
    def transcribe(self, audio_data):
        print(f"DummyWhisper: Pretending to transcribe {len(audio_data)} samples")
        return "This is a test transcription. The whisper.dll functions could not be accessed properly."

# Simple wrapper for whisper.cpp - try alternative function names
class Whisper:
    def __init__(self, model_path):
        # Check if model exists
        print(f"Checking model file: {model_path}")
        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        print(f"Loading model from: {model_path}")
        
        # Try different function names that might exist in the DLL
        init_functions = [
            'whisper_init_from_file',
            'whisper_load',
            'whisper_init',
            'whisper_init_state',
            'whisper_model_load'
        ]
        
        self.ctx = None
        for func_name in init_functions:
            try:
                if hasattr(_lib, func_name):
                    init_func = getattr(_lib, func_name)
                    init_func.restype = POINTER(whisper_context)
                    self.ctx = init_func(c_char_p(model_path.encode('utf-8')))
                    if self.ctx:
                        print(f"Successfully loaded model using {func_name}")
                        break
            except Exception as e:
                print(f"Failed to initialize with {func_name}: {e}")
        
        if not self.ctx:
            print("Error: Failed to initialize whisper context with any known function")
            raise RuntimeError("Failed to initialize whisper context. Using dummy implementation.")
    
    def transcribe(self, audio_data):
        # This is a simplified implementation
        print(f"Attempting to transcribe {len(audio_data)} samples")
        return "This is a placeholder transcription. The real transcription function is not implemented."
        
    def __del__(self):
        """Clean up resources when the object is deleted"""
        if hasattr(self, 'ctx') and self.ctx:
            try:
                if hasattr(_lib, 'whisper_free'):
                    _lib.whisper_free(self.ctx)
                    print("Whisper resources freed")
                else:
                    print("whisper_free function not found, potential memory leak")
            except Exception as e:
                print(f"Error freeing resources: {e}")

# Determine which implementation to use
try:
    # Try to create a real Whisper instance
    test_model_path = os.path.join(os.path.dirname(__file__), 'whisper.cpp', 'models', 'ggml-base.en.bin')
    if os.path.exists(test_model_path):
        _ = Whisper(test_model_path)
        WhisperImpl = Whisper
        print("Using real Whisper implementation")
    else:
        print(f"Test model not found at {test_model_path}, will use dummy implementation")
        WhisperImpl = DummyWhisper
except Exception as e:
    print(f"Error testing Whisper implementation: {e}")
    print("Falling back to dummy implementation")
    WhisperImpl = DummyWhisper