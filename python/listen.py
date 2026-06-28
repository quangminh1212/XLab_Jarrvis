#!/usr/bin/env python3
"""
Voice recording + STT helper script for MCP Voice Bridge.
Records audio from microphone using VAD, transcribes via Google Speech.

Usage: python listen.py [language] [timeout_seconds] [mic_index]
  language:        BCP-47 code (default: vi-VN)
  timeout_seconds: max wait time (default: 30)
  mic_index:       device index (-1 = default, default: -1)

Output: transcribed text on stdout (empty if nothing heard)
"""
import sys
import json
import tempfile
import os
import time
import wave

import numpy as np
import sounddevice as sd

# ── Config from CLI args ──────────────────────────────────────────────────────
LANGUAGE = sys.argv[1] if len(sys.argv) > 1 else 'vi-VN'
TIMEOUT = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
MIC_INDEX = int(sys.argv[3]) if len(sys.argv) > 3 else -1

# ── VAD / Audio constants ─────────────────────────────────────────────────────
FS = 16000          # sample rate Hz
CHUNK_SEC = 0.08    # chunk duration (80ms for responsive VAD)
SILENCE_SEC = 1.0   # silence duration to consider speech ended
MIN_SPEECH_SEC = 0.4  # minimum speech duration to bother transcribing
THRESHOLD = 0.008   # RMS threshold (post-gain)
GAIN = 20.0         # microphone gain multiplier


def record_with_vad() -> np.ndarray | None:
    """Record audio using Voice Activity Detection. Returns boosted audio array or None."""
    device = None if MIC_INDEX < 0 else MIC_INDEX
    buffer = []
    speaking = False
    silence_start = None
    start_time = time.time()

    print(f"[listen] lang={LANGUAGE} timeout={TIMEOUT}s mic={MIC_INDEX}", file=sys.stderr, flush=True)

    while time.time() - start_time < TIMEOUT:
        # Record one chunk
        chunk = sd.rec(
            int(CHUNK_SEC * FS),
            samplerate=FS,
            channels=1,
            dtype='float32',
            device=device,
        )
        sd.wait()
        chunk = chunk.flatten()

        # Apply gain + clip
        chunk_boosted = np.clip(chunk * GAIN, -1.0, 1.0)
        rms = float(np.sqrt(np.mean(chunk_boosted ** 2)))

        if rms > THRESHOLD:
            if not speaking:
                print("[listen] speech detected", file=sys.stderr, flush=True)
                speaking = True
                silence_start = None
            buffer.append(chunk_boosted)
        else:
            if speaking:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_SEC:
                    print("[listen] silence → end", file=sys.stderr, flush=True)
                    speech_dur = len(buffer) * CHUNK_SEC
                    if speech_dur >= MIN_SPEECH_SEC:
                        return np.concatenate(buffer)
                    # Too short – reset and keep listening
                    buffer = []
                    speaking = False
                    silence_start = None
            buffer.append(chunk_boosted)

    # Timeout: return whatever speech we have (if any)
    if speaking and len(buffer) * CHUNK_SEC >= MIN_SPEECH_SEC:
        return np.concatenate(buffer)
    return None


def transcribe(audio: np.ndarray) -> str | None:
    """Send WAV audio to Google Speech Recognition."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("[listen] SpeechRecognition not installed", file=sys.stderr)
        return None

    wav_path = tempfile.mktemp(suffix='.wav')
    try:
        # Save as PCM WAV (int16)
        audio_i16 = (audio * 32767).astype(np.int16)
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(FS)
            wf.writeframes(audio_i16.tobytes())

        r = sr.Recognizer()
        r.energy_threshold = 30  # low – we already applied gain
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)

        text = r.recognize_google(audio_data, language=LANGUAGE)
        return text

    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"[listen] STT error: {e}", file=sys.stderr)
        return None
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


def main():
    audio = record_with_vad()
    if audio is None:
        print("")  # empty = nothing detected
        sys.exit(0)

    text = transcribe(audio)
    print(text if text else "")


if __name__ == '__main__':
    main()
