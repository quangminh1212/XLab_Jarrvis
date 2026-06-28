#!/usr/bin/env python3
"""
Voice recording + STT helper script for MCP Voice Bridge.
Records audio from microphone using VAD, transcribes via Google Speech.

Usage: python listen.py [language] [timeout_seconds] [mic_index] [wait_for_speech]
  language:        BCP-47 code (default: vi-VN)
  timeout_seconds: max wait time (default: 30, 0 = infinite)
  mic_index:       device index (-1 = default, default: -1)
  wait_for_speech: 1 = keep listening silently until speech detected, then record until silence

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

# ── Audio chimes ──────────────────────────────────────────────────────────────
_CHIME_FS = 44100

def _chime(freq_start: float, freq_end: float, duration: float = 0.25, vol: float = 0.25):
    """Synthesize and play a short frequency-sweep chime."""
    try:
        t = np.linspace(0, duration, int(_CHIME_FS * duration), endpoint=False)
        freq = np.linspace(freq_start, freq_end, len(t))
        phase = np.cumsum(2 * np.pi * freq / _CHIME_FS)
        wave = vol * np.sin(phase)
        envelope = np.exp(-4 * t / duration)
        sd.play((wave * envelope).astype(np.float32), _CHIME_FS, blocking=True)
    except Exception:
        pass  # Never block on chime failure

def chime_listening():
    """Rising chime – mic is now active."""
    _chime(700, 1100)

def chime_done():
    """Falling chime – done recording."""
    _chime(1100, 700)

# ── Config from CLI args ──────────────────────────────────────────────────────
LANGUAGE = sys.argv[1] if len(sys.argv) > 1 else 'vi-VN'
TIMEOUT = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
MIC_INDEX = int(sys.argv[3]) if len(sys.argv) > 3 else -1
WAIT_FOR_SPEECH = bool(int(sys.argv[4])) if len(sys.argv) > 4 else False

# ── VAD / Audio constants ─────────────────────────────────────────────────────
FS = 16000          # sample rate Hz
CHUNK_SEC = 0.08    # chunk duration (80ms for responsive VAD)
SILENCE_SEC = 1.0   # silence duration to consider speech ended
MIN_SPEECH_SEC = 0.8  # minimum speech duration to bother transcribing (noise spikes are short)
THRESHOLD = 0.003   # RMS threshold (post-gain) - lowered
GAIN = 45.0         # microphone gain multiplier - increased
NOISE_FLOOR_SEC = 1.5  # warm-up period to ignore background noise at start
DYNAMIC_THRESHOLD_MULT = 1.5  # threshold = max_observed_noise * this multiplier


def record_with_vad() -> np.ndarray | None:
    """Record audio using Voice Activity Detection. Returns boosted audio array or None."""
    device = None if MIC_INDEX < 0 else MIC_INDEX
    buffer = []
    speaking = False
    silence_start = None
    start_time = time.time()
    warm_up_until = time.time() + NOISE_FLOOR_SEC
    indefinite = WAIT_FOR_SPEECH and TIMEOUT <= 0
    noise_samples = []
    threshold = THRESHOLD

    print(f"[listen] lang={LANGUAGE} wait_for_speech={WAIT_FOR_SPEECH} timeout={TIMEOUT if TIMEOUT > 0 else 'inf'}s mic={MIC_INDEX}", file=sys.stderr, flush=True)
    chime_listening()  # rising chime = mic active

    while indefinite or (time.time() - start_time < TIMEOUT):
        # Debug: print rms periodically while waiting in indefinite mode
        if WAIT_FOR_SPEECH and not speaking and time.time() > warm_up_until and (int(time.time() * 2) % 5 == 0):
            pass
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

        # Calibrate dynamic threshold from warm-up noise
        if WAIT_FOR_SPEECH and time.time() < warm_up_until:
            noise_samples.append(rms)
            if len(noise_samples) > 5:
                observed_max = float(np.max(noise_samples[-10:]))
                threshold = max(THRESHOLD, observed_max * DYNAMIC_THRESHOLD_MULT)
            print(f"[listen] warm-up rms={rms:.4f} threshold={threshold:.4f}", file=sys.stderr, flush=True)
            continue

        # Debug log during indefinite wait
        if WAIT_FOR_SPEECH and not speaking and (int(time.time() * 10) % 50 == 0):
            print(f"[listen] waiting rms={rms:.4f} threshold={threshold:.4f}", file=sys.stderr, flush=True)

        if rms > threshold:
            # Skip warm-up noise in wait_for_speech mode
            if WAIT_FOR_SPEECH and not speaking and time.time() < warm_up_until:
                continue
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
                        chime_done()  # falling chime = recording complete
                        return np.concatenate(buffer)
                    # Too short – reset and keep listening
                    buffer = []
                    speaking = False
                    silence_start = None
                    if WAIT_FOR_SPEECH:
                        warm_up_until = time.time() + NOISE_FLOOR_SEC
            buffer.append(chunk_boosted)

    # Timeout: return whatever speech we have (if any)
    if speaking and len(buffer) * CHUNK_SEC >= MIN_SPEECH_SEC:
        chime_done()
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
