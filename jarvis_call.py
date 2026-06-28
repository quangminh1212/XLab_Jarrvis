#!/usr/bin/env python3
"""
Jarvis Voice Call - Real-time AI phone call style
C:/Dev/jarvis-voice-call/jarvis_call.py

Features:
- Continuous mic listening with VAD
- Vietnamese STT
- Fast AI response (placeholder now)
- Instant voice reply (edge-tts)
- Phone call experience: speak → listen → reply → repeat

Run: C:/Python314/python.exe C:/Dev/jarvis-voice-call/jarvis_call.py
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

# ========= CONFIG =========
FS = 16000
MIC_IDX = 1              # USB Audio Device (from previous detection)
GAIN = 45.0              # Very high gain for weak mic
SILENCE_SEC = 0.9
MIN_SPEECH_SEC = 0.5
CHUNK_SEC = 0.12
THRESHOLD = 0.0025       # Low threshold

# ========= AI RESPONSE (replace later with real LLM) =========
def get_ai_response(text: str) -> str:
    text = text.lower().strip()
    
    if any(x in text for x in ["xin chào", "hello", "chào"]):
        return "Xin chào, tôi là Jarvis. Bạn cần gì?"
    if any(x in text for x in ["tên", "là ai"]):
        return "Tôi là Jarvis, trợ lý giọng nói thời gian thực."
    if any(x in text for x in ["giờ", "thời gian", "bây giờ"]):
        return f"Bây giờ là {time.strftime('%H:%M')}"
    if any(x in text for x in ["cảm ơn", "thank"]):
        return "Không có gì."
    if "tạm biệt" in text or "bye" in text:
        return "Tạm biệt. Gọi lại khi cần."
    
    # Default: echo + confirm
    return f"Bạn nói: {text}. Tôi đang lắng nghe."

# ========= AUDIO =========
def record_chunk(mic):
    audio = sd.rec(int(CHUNK_SEC * FS), samplerate=FS, channels=1, dtype='float32', device=mic)
    sd.wait()
    return audio.flatten()

def boost_normalize(audio):
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    return np.clip(audio * GAIN, -1.0, 1.0)

def to_wav(audio):
    audio = boost_normalize(audio)
    i16 = (audio * 32767).astype(np.int16)
    p = tempfile.mktemp(suffix='.wav')
    with wave.open(p, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FS)
        w.writeframes(i16.tobytes())
    return p

# ========= LISTEN (VAD) =========
def listen_until_speech(mic):
    buffer = []
    speaking = False
    silence_start = None
    
    while True:
        chunk = record_chunk(mic)
        rms = np.sqrt(np.mean(chunk**2))
        
        if rms > THRESHOLD:
            if not speaking:
                print("[Bắt đầu nói]")
                speaking = True
            buffer.append(chunk)
            silence_start = None
        else:
            if speaking:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_SEC:
                    print("[Kết thúc]")
                    if len(buffer) * CHUNK_SEC >= MIN_SPEECH_SEC:
                        return np.concatenate(buffer)
                    else:
                        return None
            buffer.append(chunk)
        time.sleep(0.01)

# ========= STT =========
def stt(wav_path):
    r = sr.Recognizer()
    r.energy_threshold = 30
    try:
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
            return r.recognize_google(audio, language='vi-VN')
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"STT lỗi: {e}")
        return None
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)

# ========= TTS =========
async def speak(text: str):
    try:
        communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
        path = tempfile.mktemp(suffix=".mp3")
        await communicate.save(path)
        os.system(f'start /min "" "{path}"')  # Windows media player
        await asyncio.sleep(0.3)
    except Exception as e:
        print(f"TTS lỗi: {e}")

# ========= MAIN LOOP =========
async def main():
    print("=== JARVIS VOICE CALL (Phone style) ===")
    print(f"Mic: {sd.query_devices(MIC_IDX)['name']}")
    print("Nói như đang gọi điện. Jarvis sẽ nghe và trả lời bằng giọng nói.")
    print("Nhấn Ctrl+C để kết thúc.\n")
    
    mic = MIC_IDX
    
    while True:
        try:
            audio = listen_until_speech(mic)
            if audio is None:
                continue
            
            wav = to_wav(audio)
            text = stt(wav)
            
            if text:
                print(f"👂 Bạn: {text}")
                response = get_ai_response(text)
                print(f"🤖 Jarvis: {response}")
                await speak(response)
                print("---\n")
            else:
                print("(Không nhận diện được)")
        except KeyboardInterrupt:
            print("\nKết thúc cuộc gọi.")
            await speak("Tạm biệt.")
            break
        except Exception as e:
            print(f"Lỗi: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())