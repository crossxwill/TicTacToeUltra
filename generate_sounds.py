"""Generate sound effects for Ultimate Tic Tac Toe."""

import numpy as np
import wave
import struct
import os

SAMPLE_RATE = 44100

def save_wav(filename, samples, volume=0.8):
    """Save samples as a WAV file."""
    # Normalize and convert to 16-bit integers
    samples = np.array(samples)
    # Use provided volume
    samples = samples / np.max(np.abs(samples)) * volume
    samples = (samples * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(samples.tobytes())

def generate_win_sound():
    """Generate a softer triumphant fanfare."""
    duration = 1.5
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Lower octave for less piercing sound
    frequencies = [262, 330, 392, 523]  # C4, E4, G4, C5
    samples = np.zeros_like(t)

    for i, freq in enumerate(frequencies):
        start = i * 0.15
        end = start + 0.5
        mask = (t >= start) & (t < end)
        note_t = t[mask] - start
        # Softer attack (0.1s decay instead of 50)
        envelope = np.exp(-note_t * 6) * (1 - np.exp(-note_t * 15)) 
        
        # Fundamental
        samples[mask] += np.sin(2 * np.pi * freq * note_t) * envelope
        # Add rich harmonics for "electric piano" feel
        samples[mask] += 0.5 * np.sin(2 * np.pi * freq * 2 * note_t) * envelope * 0.5
        samples[mask] += 0.25 * np.sin(2 * np.pi * freq * 3 * note_t) * envelope * 0.3

    # Final sustained chord
    start = 0.6
    mask = t >= start
    chord_t = t[mask] - start
    envelope = np.exp(-chord_t * 2) * (1 - np.exp(-chord_t * 10))
    for freq in [262, 330, 392, 523]:
        samples[mask] += 0.3 * np.sin(2 * np.pi * freq * chord_t) * envelope

    return samples

def generate_sad_sound():
    """Generate a softer sad descending sound."""
    duration = 1.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Lower frequencies
    frequencies = [293, 261, 246, 196] # D4, C4, B3, G3
    samples = np.zeros_like(t)

    for i, freq in enumerate(frequencies):
        start = i * 0.25
        end = start + 0.35
        mask = (t >= start) & (t < end)
        note_t = t[mask] - start
        envelope = np.exp(-note_t * 3) * (1 - np.exp(-note_t * 10))
        
        samples[mask] += np.sin(2 * np.pi * freq * note_t) * envelope
        # Less vibrato
        vibrato = 1 + 0.01 * np.sin(2 * np.pi * 4 * note_t)
        samples[mask] += 0.2 * np.sin(2 * np.pi * freq * 0.5 * note_t * vibrato) * envelope

    return samples

def generate_stamp_sound():
    """Generate a stamp/thud sound."""
    duration = 0.4
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Impact sound - low frequency thud
    freq = 80
    envelope = np.exp(-t * 15) * (1 - np.exp(-t * 500))
    samples = np.sin(2 * np.pi * freq * t) * envelope

    # Add higher frequency click at the start
    click_envelope = np.exp(-t * 80)
    samples += 0.5 * np.sin(2 * np.pi * 300 * t) * click_envelope
    samples += 0.3 * np.sin(2 * np.pi * 500 * t) * click_envelope

    # Add some noise for texture
    noise = np.random.randn(len(t)) * np.exp(-t * 30) * 0.2
    samples += noise

    return samples


def generate_click_sound():
    """Generate a pleasing 'thock' sound instead of sharp click."""
    duration = 0.1
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Lower frequency for "thock"
    click_freq = 600 # Was 1800
    envelope = np.exp(-t * 60) * (1 - np.exp(-t * 500))
    samples = np.sin(2 * np.pi * click_freq * t) * envelope * 0.8

    # Wood-like body
    thock_freq = 300
    thock_envelope = np.exp(-t * 40)
    samples += np.sin(2 * np.pi * thock_freq * t) * thock_envelope * 0.6

    return samples

def main():
    sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
    os.makedirs(sounds_dir, exist_ok=True)

    print("Generating win sound...")
    save_wav(os.path.join(sounds_dir, 'win.wav'), generate_win_sound(), volume=0.5)

    print("Generating sad sound...")
    save_wav(os.path.join(sounds_dir, 'sad.wav'), generate_sad_sound(), volume=0.5)

    print("Generating stamp sound...")
    save_wav(os.path.join(sounds_dir, 'stamp.wav'), generate_stamp_sound(), volume=0.8)

    print("Generating click sound...")
    save_wav(os.path.join(sounds_dir, 'click.wav'), generate_click_sound(), volume=0.5)

    print("All sounds generated successfully!")

if __name__ == "__main__":
    main()
