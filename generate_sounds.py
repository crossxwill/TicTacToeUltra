"""Generate sound effects for Ultimate Tic Tac Toe."""

import numpy as np
import wave
import struct
import os

SAMPLE_RATE = 44100

def save_wav(filename, samples):
    """Save samples as a WAV file."""
    # Normalize and convert to 16-bit integers
    samples = np.array(samples)
    samples = samples / np.max(np.abs(samples)) * 0.8
    samples = (samples * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(samples.tobytes())

def generate_win_sound():
    """Generate a triumphant fanfare sound."""
    duration = 1.5
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Triumphant ascending notes (C-E-G-C chord arpeggio)
    frequencies = [262, 330, 392, 523]  # C4, E4, G4, C5
    samples = np.zeros_like(t)

    for i, freq in enumerate(frequencies):
        start = i * 0.15
        end = start + 0.5
        mask = (t >= start) & (t < end)
        note_t = t[mask] - start
        envelope = np.exp(-note_t * 3) * (1 - np.exp(-note_t * 50))
        samples[mask] += np.sin(2 * np.pi * freq * note_t) * envelope
        # Add harmonics for richness
        samples[mask] += 0.3 * np.sin(2 * np.pi * freq * 2 * note_t) * envelope
        samples[mask] += 0.15 * np.sin(2 * np.pi * freq * 3 * note_t) * envelope

    # Final sustained chord
    start = 0.6
    mask = t >= start
    chord_t = t[mask] - start
    envelope = np.exp(-chord_t * 1.5) * (1 - np.exp(-chord_t * 30))
    for freq in [262, 330, 392, 523]:
        samples[mask] += 0.4 * np.sin(2 * np.pi * freq * chord_t) * envelope

    return samples

def generate_sad_sound():
    """Generate a sad descending sound."""
    duration = 1.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Sad descending notes
    samples = np.zeros_like(t)

    # Descending minor notes
    frequencies = [392, 349, 330, 262]  # G4, F4, E4, C4 (descending)

    for i, freq in enumerate(frequencies):
        start = i * 0.25
        end = start + 0.35
        mask = (t >= start) & (t < end)
        note_t = t[mask] - start
        envelope = np.exp(-note_t * 4) * (1 - np.exp(-note_t * 40))
        # Use triangle wave for sadder sound
        samples[mask] += np.sin(2 * np.pi * freq * note_t) * envelope
        # Add slight vibrato
        vibrato = 1 + 0.02 * np.sin(2 * np.pi * 5 * note_t)
        samples[mask] += 0.3 * np.sin(2 * np.pi * freq * 0.5 * note_t * vibrato) * envelope

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
    """Generate a keyboard/mechanical click sound."""
    duration = 0.08
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Sharp attack click
    click_freq = 1800
    envelope = np.exp(-t * 120) * (1 - np.exp(-t * 2000))
    samples = np.sin(2 * np.pi * click_freq * t) * envelope * 0.6

    # Add lower thock component
    thock_freq = 400
    thock_envelope = np.exp(-t * 80) * (1 - np.exp(-t * 1500))
    samples += np.sin(2 * np.pi * thock_freq * t) * thock_envelope * 0.4

    # Add some high frequency noise for realism
    noise = np.random.randn(len(t)) * np.exp(-t * 150) * 0.15
    samples += noise

    return samples

def main():
    sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
    os.makedirs(sounds_dir, exist_ok=True)

    print("Generating win sound...")
    save_wav(os.path.join(sounds_dir, 'win.wav'), generate_win_sound())

    print("Generating sad sound...")
    save_wav(os.path.join(sounds_dir, 'sad.wav'), generate_sad_sound())

    print("Generating stamp sound...")
    save_wav(os.path.join(sounds_dir, 'stamp.wav'), generate_stamp_sound())

    print("Generating click sound...")
    save_wav(os.path.join(sounds_dir, 'click.wav'), generate_click_sound())

    print("All sounds generated successfully!")

if __name__ == "__main__":
    main()
