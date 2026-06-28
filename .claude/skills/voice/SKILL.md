---
name: voice
description: Chon ngon ngu / giong noi cho Jarrvis
user_invocable: true
argument-hint: "[language code]"
---

Giup user chon ngon ngu va giong noi cho Jarrvis TTS (edge-tts neural voices).
Neu user cung cap ma ngon ngu qua $ARGUMENTS, xac nhan lua chon do.
Neu khong, hien thi danh sach duoi va hoi ho muon chon gi.

## Ngon ngu va giong noi ho tro

| Ma ngon ngu | Ten | Giong |
|---|---|---|
| `vi-VN` | Tieng Viet (mac dinh) | HoaiMyNeural |
| `en-US` | English (My) | AriaNeural |
| `en-GB` | English (Anh) | SoniaNeural |
| `ja-JP` | Nhat | NanamiNeural |
| `zh-CN` | Trung Quoc | XiaoxiaoNeural |
| `ko-KR` | Han Quoc | SunHiNeural |

## Huong dan su dung

De doi ngon ngu, dung `voice_speak` voi tham so `language`:
- `voice_speak(text="...", language="en-US")` -> Tieng Anh
- `voice_speak(text="...", language="vi-VN")` -> Tieng Viet

Sau khi user chon, hay thu bang cach goi `voice_speak` voi mot cau ngan mau trong ngon ngu do.
Nhac ho co the thay doi bat cu luc nao bang lenh `/voice`.
