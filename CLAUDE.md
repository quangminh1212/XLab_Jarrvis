# CLAUDE.md

This file provides guidance to Claude Code (and other MCP-compatible agents) when working with this repository.

## Project Overview

**Jarrvis** is a bidirectional voice MCP server for Windows.
It exposes four tools — `voice_listen`, `voice_speak`, `voice_ask`, `list_audio_devices` — enabling AI agents to have real voice conversations with the user via microphone and speakers.

## Quick Start

```bash
npm install
node bin/mcp-voice-bridge.js   # starts the MCP stdio server
```

The repo includes `.mcp.json`, so Claude Code auto-discovers the server when opened from this directory:
```bash
cd XLab_Jarrvis
claude
```

## Architecture

**Node.js MCP server** (`src/server.js`) communicates over stdio (JSON-RPC 2.0).
Audio I/O happens via **Python subprocesses** in the `python/` directory.

```
voice_listen  → python/listen.py   → sounddevice (VAD) + Google STT
voice_speak   → python/speak.py    → edge-tts (Microsoft neural) + Windows SAPI fallback
voice_ask     → speak.py + listen.py (sequential)
list_audio_devices → python/devices.py → sounddevice.query_devices()
```

**IMPORTANT — stdout is sacred:**
Never log to stdout in `src/server.js`. All debug output must go to stderr.
The MCP stdio protocol uses stdout exclusively for JSON-RPC messages.

## Commands

```bash
npm start                  # Run MCP server
npm run test:devices       # List audio devices
npm run test:speak         # Test TTS output
npm run test:listen        # Test mic recording + STT
```

## Tools

| Tool | Description |
|------|-------------|
| `voice_speak(text, language?)` | Speak text to user (TTS) |
| `voice_listen(timeout_seconds?, language?)` | Record mic + transcribe (STT) |
| `voice_ask(question, timeout_seconds?, language?)` | Speak question, wait for spoken answer |
| `list_audio_devices()` | List microphones and speakers |

## Supported Languages (BCP-47)

`vi-VN` (default), `en-US`, `en-GB`, `ja-JP`, `zh-CN`, `ko-KR`

## Slash Commands (Claude Code Skills)

- `/listen` — activate microphone and listen to user
- `/voice [lang]` — change TTS language/voice

## Configuration

Set environment variables to customize behavior:

| Variable | Default | Description |
|---|---|---|
| `VOICE_LANGUAGE` | `vi-VN` | Default language |
| `VOICE_MIC_INDEX` | `-1` | Microphone device index |
| `VOICE_PYTHON` | `python` | Python executable path |

## Dependencies

**Node.js:** `@modelcontextprotocol/sdk`, `dotenv`

**Python (must be installed):**
```bash
pip install sounddevice numpy SpeechRecognition edge-tts
```

## Key Constraints

- **Windows only for TTS playback** (uses PowerShell `System.Windows.Media.MediaPlayer`)
- Falls back to Windows SAPI if edge-tts playback fails
- STT uses Google Speech Recognition (requires internet)
- No sox, ffmpeg, or external audio tools required
