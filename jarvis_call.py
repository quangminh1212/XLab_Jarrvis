#!/usr/bin/env python3
"""
Jarvis Voice Call - Real-time AI conversation like a phone call
C:/Dev/jarvis-voice-call/jarvis_call.py

Speak → AI listens → AI thinks → speaks back → repeat
"""

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import tempfile
import os
import time
import wave
import asyncio
import edge_tts

# Config
FS = 16000
MIC_IDX = 1              # USB mic
GAIN = 35.0
SILENCE_SEC = 1.0
MIN_SPEECH_SEC = 0.6
CHUNK_SEC = 0.15

# Placeholder AI response (replace with real AI later)
def get_ai_response(text: str) -> str:
    """Simple echo + demo. Replace with real LLM call."""
    if "tên" in text.lower() or "name" in text.lower():
        return "Tôi là Jarvis, trợ lý giọng nói của bạn."
    if "thời gian" in text.lower() or "giờ" in text.lower():
        return "Bây giờ là " + time.strftime("%H:%M")
    return f"Bạn vừa nói: {text}. Tôi đang nghe."

async def speak(text: str):
    """TTS with edge-tts (good Vietnamese voice)"""
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        path = tmp.name
    await communicate.save(path)
    os.system(f'start /min wmplayer "{path}"')   # Windows play
    await asyncio.sleep(0.5)  # let it start
    # Note: player runs in background, file cleaned later if needed

def record_chunk(mic):
    a = sd.rec(int(CHUNK_SEC * FS), samplerate=FS, channels=1, dtype='float32', device=mic)
    sd.wait()
    return a.flatten()

def to_wav(audio):
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    audio = np.clip(audio * GAIN, -1.0, 1.0)
    i16 = (audio * 32767).astype(np.int16)
    p = tempfile.mktemp(suffix='.wav')
    with wave.open(p, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FS)
        w.writeframes(i16.tobytes())
    return p

def listen_until_speech(mic):
    """Energy-based VAD + capture full phrase"""
    buffer = []
    speaking = False
    silence_start = None
    
    while True:
        chunk = record_chunk(mic)
        rms = np.sqrt(np.mean(chunk**2))
        
        if rms > 0.003:  # low threshold
            if not speaking:
                print("[START]")
                speaking = True
            buffer.append(chunk)
            silence_start = None
        else:
            if speaking:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_SEC:
                    print("[END]")
                    return np.concatenate(buffer) if buffer else None
            buffer.append(chunk)
        
        time.sleep(0.01)

def stt(wav_path):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
            return r.recognize_google(audio, language='vi-VN')
    except:
        return None
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)

async def main():
    print("=== JARVIS VOICE CALL ===")
    print("Mic:", sd.query_devices(MIC_IDX)['name'])
    print("Speak like on a phone call. Ctrl+C to end.\n")
    
    mic = MIC_IDX
    
    while True:
        try:
            audio = listen_until_speech(mic)
            if audio is None or len(audio) < int(MIN_SPEECH_SEC * FS):
                continue
            
            wav = to_wav(audio)
            text = stt(wav)
            
            if text:
                print(f"👂 Bạn: {text}")
                response = get_ai_response(text)
                print(f"🤖 Jarvis: {response}")
                await speak(response)
                print("---\n")
        except KeyboardInterrupt:
            print("\nCall ended.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())