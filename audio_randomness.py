import hashlib
import time
import pyaudio
import numpy as np

DEBUG = False
def generate_random_key_from_audio(duration=3, sample_rate=44100):
    if DEBUG: print(f"Capturing audio data for {duration} seconds...")
    p = pyaudio.PyAudio()
    chunk = 1024
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=chunk)
    
    frames = []
    total_frames = int(sample_rate / chunk * duration)
    
    for _ in range(total_frames):
        try:
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
        except IOError:
            if DEBUG: print("Error reading audio stream")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    audio_data = b''.join(frames)
    return hashlib.sha256(audio_data).digest()
