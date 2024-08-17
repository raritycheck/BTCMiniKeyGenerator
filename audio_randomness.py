import hashlib
import time
import pyaudio
import numpy as np
import os

DEBUG = False

def generate_random_key_from_audio(duration=3, sample_rate=44100, min_frames=10):
    if DEBUG: 
        print(f"Capturing audio data for {duration} seconds...")
    
    p = pyaudio.PyAudio()
    chunk = 1024
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=chunk)
    
    frames = []
    total_frames = int(sample_rate / chunk * duration)
    frame_count = 0

    for _ in range(total_frames):
        try:
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
            frame_count += 1
        except IOError as e:
            if DEBUG: 
                print(f"Error reading audio stream: {e}")
            continue
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    if frame_count < min_frames:
        raise ValueError("Insufficient audio data captured. Try increasing the duration or ensuring the microphone is working properly.")
    
    audio_data = b''.join(frames)

    # Combine audio data with system randomness for additional entropy
    system_entropy = os.urandom(32)
    combined_data = audio_data + system_entropy
    
    return hashlib.sha256(combined_data).digest()

