#!/usr/bin/env python3
"""
TTS helper script for MCP Voice Bridge.
Speaks text aloud using edge-tts (high quality) with Windows SAPI fallback.

Usage: python speak.py "text to speak" [language_code]
  language_code: vi-VN (default), en-US, en-GB, ja-JP, zh-CN, etc.

Exit code 0 = success, prints "OK" to stdout.
"""
import sys
import asyncio
import tempfile
import subprocess
import os
import time

VOICE_MAP = {
    'vi-VN': 'vi-VN-HoaiMyNeural',
    'vi': 'vi-VN-HoaiMyNeural',
    'en-US': 'en-US-AriaNeural',
    'en': 'en-US-AriaNeural',
    'en-GB': 'en-GB-SoniaNeural',
    'ja-JP': 'ja-JP-NanamiNeural',
    'ja': 'ja-JP-NanamiNeural',
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
    'ko-KR': 'ko-KR-SunHiNeural',
    'ko': 'ko-KR-SunHiNeural',
}


def play_mp3_windows(path: str) -> bool:
    """Play MP3 file synchronously on Windows using PowerShell MediaPlayer."""
    abs_path = os.path.abspath(path).replace('\\', '/')
    ps_script = f"""
try {{
    Add-Type -AssemblyName PresentationCore
    $player = New-Object System.Windows.Media.MediaPlayer
    $player.Open([Uri]"file:///{abs_path}")
    $player.Play()
    Start-Sleep -Milliseconds 800
    $dur = $player.NaturalDuration
    if ($dur.HasTimeSpan) {{
        Start-Sleep -Milliseconds ([int]$dur.TimeSpan.TotalMilliseconds + 400)
    }} else {{
        Start-Sleep -Seconds 5
    }}
    $player.Close()
    exit 0
}} catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
"""
    result = subprocess.run(
        ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_script],
        capture_output=True, text=True, timeout=120
    )
    return result.returncode == 0


def speak_sapi(text: str) -> None:
    """Fallback: Windows built-in SAPI TTS (no external deps required)."""
    safe = text.replace('"', "'").replace('`', '').replace('$', '').replace('\n', ' ')
    ps_cmd = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        f'$s.Speak("{safe}")'
    )
    subprocess.run(
        ['powershell', '-NoProfile', '-Command', ps_cmd],
        capture_output=True, timeout=120
    )


async def speak_edge_tts(text: str, voice: str) -> bool:
    """High-quality TTS via Microsoft Edge neural voices."""
    try:
        import edge_tts
    except ImportError:
        print("edge-tts not installed, falling back to SAPI", file=sys.stderr)
        return False

    output = tempfile.mktemp(suffix='.mp3')
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output)
        success = play_mp3_windows(output)
        if not success:
            # Fallback: use os.startfile and estimate wait time
            os.startfile(os.path.abspath(output))
            file_size = os.path.getsize(output)
            # Rough estimate: ~16KB/s for 64kbps MP3
            wait_sec = max(3, file_size / 8000)
            time.sleep(wait_sec)
        return True
    except Exception as e:
        print(f"edge-tts error: {e}", file=sys.stderr)
        return False
    finally:
        if os.path.exists(output):
            try:
                os.unlink(output)
            except Exception:
                pass


def main():
    if len(sys.argv) < 2:
        print("Usage: speak.py <text> [language]", file=sys.stderr)
        sys.exit(1)

    text = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'vi-VN'
    voice = VOICE_MAP.get(lang, lang)

    # Try edge-tts (best quality)
    success = asyncio.run(speak_edge_tts(text, voice))

    if not success:
        # Fallback to Windows SAPI
        print("Using SAPI fallback", file=sys.stderr)
        speak_sapi(text)

    print("OK")


if __name__ == '__main__':
    main()
