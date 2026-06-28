# jarrvis

> MCP server cho phép AI agents (Claude Code, Codex, Devin, ...) nói chuyện trực tiếp với bạn qua **microphone** và **loa**.

## Tính năng

- **`voice_speak`** – Agent đọc văn bản cho bạn nghe (TTS)
- **`voice_listen`** – Agent lắng nghe giọng nói của bạn qua mic, trả về văn bản
- **`voice_ask`** – Agent hỏi câu hỏi bằng giọng nói rồi chờ bạn trả lời
- **`list_audio_devices`** – Liệt kê tất cả thiết bị âm thanh trên máy
- Hỗ trợ **tiếng Việt** (mặc định), tiếng Anh, Nhật, Hoa, Hàn
- TTS dùng **edge-tts** (giọng Microsoft neural, miễn phí) với fallback về Windows SAPI
- STT dùng **Google Speech Recognition** (miễn phí, cần internet)
- VAD (Voice Activity Detection) tự động phát hiện khi bạn nói / dừng

## Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|---|---|
| Node.js | ≥ 18 |
| Python | ≥ 3.9 |
| OS | Windows 10+ (TTS WPF) / Linux / macOS |

### Python packages (cài sẵn hoặc cài qua pip)

```bash
pip install sounddevice numpy SpeechRecognition edge-tts
```

## Cài đặt

```bash
git clone <repo>
cd XLab_Jarrvis
npm install
```

## Cấu hình (.env)

```bash
cp .env.example .env
# Chỉnh VOICE_LANGUAGE, VOICE_MIC_INDEX nếu cần
```

## Chạy thử

```bash
# Kiểm tra thiết bị âm thanh
npm run test:devices

# Thử TTS (Jarrvis sẽ lên tiếng)
npm run test:speak

# Thử ghi âm + nhận dạng (nói sau khi thấy [Listening...])
npm run test:listen
```

---

## Tích hợp với AI Agents

Repo đã có sẵn **config files cho tất cả CLI agents** — chỉ cần `cd XLab_Jarrvis` rồi khởi động agent là tự động load.

### Agents tự động nhận diện (Auto-discovery)

| Agent | Cách dùng | File config tự động |
|-------|-----------|---------------------|
| **Claude Code** | `claude` | `.mcp.json` + `.claude/` |
| **OpenAI Codex** | `codex` | `.codex/config.toml` |
| **Mistral Vibe** | `vibe` | `.vibe/config.toml` |
| **Gemini CLI** | `gemini` | `.gemini/settings.json` |
| **Goose** | `goose` | `.goose/config.yaml` |
| **OpenCode** | `opencode` | `opencode.json` |
| **Cursor** | Mở project folder | `.cursor/mcp.json` |
| **Windsurf / Devin** | Mở project | `.mcp.json` |

### Hermes (NousResearch) — cần cấu hình global

Hermes chưa hỗ trợ project-level config. Thêm vào `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  jarrvis:
    command: node
    args:
      - C:/Dev/XLab_Jarrvis/bin/mcp-voice-bridge.js
    env:
      PYTHONUTF8: "1"
      PYTHONIOENCODING: "utf-8"
```

Hoặc dùng CLI (từ thư mục dự án):
```bash
hermes mcp add jarrvis node bin/mcp-voice-bridge.js
```

### OpenClaw — cần cấu hình global

```bash
# Chạy từ thư mục dự án
openclaw mcp add jarrvis --command "node" --args "bin/mcp-voice-bridge.js" \
  --env PYTHONUTF8=1 --env PYTHONIOENCODING=utf-8

# Kiểm tra
openclaw mcp status
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "jarrvis": {
      "command": "node",
      "args": ["C:/Dev/XLab_Jarrvis/bin/mcp-voice-bridge.js"],
      "env": { "VOICE_LANGUAGE": "vi-VN" }
    }
  }
}
```

Vị trí:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

---

## Tools API

### `voice_speak`
| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `text` | string | Có | Văn bản cần đọc |
| `language` | string | Không | Mã ngôn ngữ BCP-47 (mặc định: `vi-VN`) |

### `voice_listen`
| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `timeout_seconds` | number | Không | Thời gian chờ tối đa (mặc định: 30) |
| `language` | string | Không | Mã ngôn ngữ nhận dạng (mặc định: `vi-VN`) |

### `voice_ask`
| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `question` | string | Có | Câu hỏi sẽ được đọc cho user nghe |
| `timeout_seconds` | number | Không | Thời gian chờ câu trả lời (mặc định: 30) |
| `language` | string | Không | Mã ngôn ngữ (mặc định: `vi-VN`) |

### `list_audio_devices`
Không có tham số. Trả về danh sách thiết bị âm thanh trên máy.

---

## Ngôn ngữ được hỗ trợ

| Code | Ngôn ngữ | Giọng edge-tts |
|---|---|---|
| `vi-VN` | Tiếng Việt | HoaiMyNeural |
| `en-US` | English (US) | AriaNeural |
| `en-GB` | English (UK) | SoniaNeural |
| `ja-JP` | 日本語 | NanamiNeural |
| `zh-CN` | 中文 | XiaoxiaoNeural |
| `ko-KR` | 한국어 | SunHiNeural |

---

## Cấu trúc dự án

```
jarrvis/
├── bin/
│   └── mcp-voice-bridge.js   # CLI entry point (MCP stdio server)
├── src/
│   ├── server.js             # MCP Server logic
│   └── config.js             # Cấu hình từ env
├── python/
│   ├── speak.py              # TTS: edge-tts + Windows SAPI fallback
│   ├── listen.py             # STT: sounddevice VAD + Google Speech
│   └── devices.py            # Liệt kê audio devices
├── jarvis_call.py            # Script Python gốc (standalone demo)
├── package.json
└── .env.example
```

## Biến môi trường

| Biến | Mặc định | Mô tả |
|---|---|---|
| `VOICE_PYTHON` | `python` | Đường dẫn Python executable |
| `VOICE_LANGUAGE` | `vi-VN` | Ngôn ngữ mặc định |
| `VOICE_MIC_INDEX` | `-1` | Index microphone (-1 = mặc định hệ thống) |
| `VOICE_TTS_VOICE` | auto | Override giọng edge-tts |
