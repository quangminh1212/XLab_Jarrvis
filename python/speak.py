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
    # Vietnamese
    'vi-VN': 'vi-VN-HoaiMyNeural',
    'vi': 'vi-VN-HoaiMyNeural',
    # English
    'en-US': 'en-US-AriaNeural',
    'en': 'en-US-AriaNeural',
    'en-GB': 'en-GB-SoniaNeural',
    'en-AU': 'en-AU-NatashaNeural',
    'en-CA': 'en-CA-ClaraNeural',
    'en-IN': 'en-IN-NeerjaNeural',
    'en-IE': 'en-IE-EmilyNeural',
    'en-ZA': 'en-ZA-LeahNeural',
    'en-NZ': 'en-NZ-MollyNeural',
    'en-PH': 'en-PH-RosaNeural',
    'en-SG': 'en-SG-LunaNeural',
    # Chinese
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
    'zh-TW': 'zh-TW-HsiaoChenNeural',
    'zh-HK': 'zh-HK-HiuMaanNeural',
    # Japanese
    'ja-JP': 'ja-JP-NanamiNeural',
    'ja': 'ja-JP-NanamiNeural',
    # Korean
    'ko-KR': 'ko-KR-SunHiNeural',
    'ko': 'ko-KR-SunHiNeural',
    # French
    'fr-FR': 'fr-FR-DeniseNeural',
    'fr': 'fr-FR-DeniseNeural',
    'fr-CA': 'fr-CA-SylvieNeural',
    'fr-CH': 'fr-CH-AurelieNeural',
    'fr-BE': 'fr-BE-CharlineNeural',
    # German
    'de-DE': 'de-DE-KatjaNeural',
    'de': 'de-DE-KatjaNeural',
    'de-AT': 'de-AT-IngridNeural',
    'de-CH': 'de-CH-LeniNeural',
    # Spanish
    'es-ES': 'es-ES-ElviraNeural',
    'es': 'es-ES-ElviraNeural',
    'es-MX': 'es-MX-DaliaNeural',
    'es-US': 'es-US-PalomaNeural',
    'es-AR': 'es-AR-ElenaNeural',
    'es-CO': 'es-CO-SalomeNeural',
    'es-CL': 'es-CL-CatalinaNeural',
    # Italian
    'it-IT': 'it-IT-ElsaNeural',
    'it': 'it-IT-ElsaNeural',
    # Portuguese
    'pt-PT': 'pt-PT-RaquelNeural',
    'pt': 'pt-PT-RaquelNeural',
    'pt-BR': 'pt-BR-FranciscaNeural',
    # Russian
    'ru-RU': 'ru-RU-SvetlanaNeural',
    'ru': 'ru-RU-SvetlanaNeural',
    # Dutch
    'nl-NL': 'nl-NL-ColetteNeural',
    'nl': 'nl-NL-ColetteNeural',
    'nl-BE': 'nl-BE-ArnaudNeural',
    # Polish
    'pl-PL': 'pl-PL-ZofiaNeural',
    'pl': 'pl-PL-ZofiaNeural',
    # Swedish
    'sv-SE': 'sv-SE-SofieNeural',
    'sv': 'sv-SE-SofieNeural',
    # Norwegian
    'nb-NO': 'nb-NO-PernilleNeural',
    'no': 'nb-NO-PernilleNeural',
    # Danish
    'da-DK': 'da-DK-ChristelNeural',
    'da': 'da-DK-ChristelNeural',
    # Finnish
    'fi-FI': 'fi-FI-SelmaNeural',
    'fi': 'fi-FI-SelmaNeural',
    # Czech
    'cs-CZ': 'cs-CZ-VlastaNeural',
    'cs': 'cs-CZ-VlastaNeural',
    # Greek
    'el-GR': 'el-GR-AthinaNeural',
    'el': 'el-GR-AthinaNeural',
    # Turkish
    'tr-TR': 'tr-TR-EmelNeural',
    'tr': 'tr-TR-EmelNeural',
    # Arabic
    'ar-SA': 'ar-SA-ZariyahNeural',
    'ar': 'ar-SA-ZariyahNeural',
    'ar-EG': 'ar-EG-SalmaNeural',
    'ar-AE': 'ar-AE-FatimaNeural',
    # Hebrew
    'he-IL': 'he-IL-HilaNeural',
    'he': 'he-IL-HilaNeural',
    # Hindi
    'hi-IN': 'hi-IN-SwaraNeural',
    'hi': 'hi-IN-SwaraNeural',
    # Bengali
    'bn-IN': 'bn-IN-TanishaaNeural',
    'bn': 'bn-IN-TanishaaNeural',
    # Tamil
    'ta-IN': 'ta-IN-PallaviNeural',
    'ta': 'ta-IN-PallaviNeural',
    # Telugu
    'te-IN': 'te-IN-ShrutiNeural',
    'te': 'te-IN-ShrutiNeural',
    # Thai
    'th-TH': 'th-TH-PremwadeeNeural',
    'th': 'th-TH-PremwadeeNeural',
    # Indonesian
    'id-ID': 'id-ID-GadisNeural',
    'id': 'id-ID-GadisNeural',
    # Malay
    'ms-MY': 'ms-MY-YasminNeural',
    'ms': 'ms-MY-YasminNeural',
    # Filipino
    'fil-PH': 'fil-PH-BlessicaNeural',
    'fil': 'fil-PH-BlessicaNeural',
    # Ukrainian
    'uk-UA': 'uk-UA-PolinaNeural',
    'uk': 'uk-UA-PolinaNeural',
    # Romanian
    'ro-RO': 'ro-RO-AlinaNeural',
    'ro': 'ro-RO-AlinaNeural',
    # Hungarian
    'hu-HU': 'hu-HU-NoemiNeural',
    'hu': 'hu-HU-NoemiNeural',
    # Slovak
    'sk-SK': 'sk-SK-ViktoriaNeural',
    'sk': 'sk-SK-ViktoriaNeural',
    # Bulgarian
    'bg-BG': 'bg-BG-KalinaNeural',
    'bg': 'bg-BG-KalinaNeural',
    # Croatian
    'hr-HR': 'hr-HR-GabrijelaNeural',
    'hr': 'hr-HR-GabrijelaNeural',
    # Catalan
    'ca-ES': 'ca-ES-JoanaNeural',
    'ca': 'ca-ES-JoanaNeural',
    # Finnish already above
    # Latin American Spanish variants
    'es-PE': 'es-PE-CamilaNeural',
    'es-VE': 'es-VE-PaolaNeural',
    'es-UY': 'es-UY-ValentinaNeural',
    'es-PR': 'es-PR-KarinaNeural',
    'es-DO': 'es-DO-RamonaNeural',
    'es-EC': 'es-EC-AndreaNeural',
    'es-GT': 'es-GT-MartaNeural',
    'es-BO': 'es-BO-MarcelaNeural',
    'es-PY': 'es-PY-TaniaNeural',
    'es-CR': 'es-CR-MariaNeural',
    'es-PA': 'es-PA-MargaritaNeural',
    'es-HN': 'es-HN-KarlaNeural',
    'es-NI': 'es-NI-YolandaNeural',
    'es-SV': 'es-SV-LorenaNeural',
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
