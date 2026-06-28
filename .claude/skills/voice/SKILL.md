---
name: voice
description: Chon ngon ngu / giong noi cho Jarrvis
user_invocable: true
argument-hint: "[language code]"
---

Giup user chon ngon ngu va giong noi cho Jarrvis TTS (edge-tts neural voices).
Neu user cung cap ma ngon ngu qua $ARGUMENTS, xac nhan lua chon do.
Neu khong, hien thi danh sach duoi va hoi ho muon chon gi.

## Danh sach ngon ngu ho tro (40+)

### Chau A
| Ma | Ngon ngu | Giong edge-tts |
|---|---|---|
| `vi-VN` | Tieng Viet (mac dinh) | HoaiMyNeural |
| `zh-CN` | Tieng Trung (Gian the) | XiaoxiaoNeural |
| `zh-TW` | Tieng Trung (Phồn thể) | HsiaoChenNeural |
| `zh-HK` | Tieng Trung (Hong Kong) | HiuMaanNeural |
| `ja-JP` | Tieng Nhat | NanamiNeural |
| `ko-KR` | Tieng Han | SunHiNeural |
| `hi-IN` | Tieng Hindi | SwaraNeural |
| `bn-IN` | Tieng Bengali | TanishaaNeural |
| `ta-IN` | Tieng Tamil | PallaviNeural |
| `te-IN` | Tieng Telugu | ShrutiNeural |
| `th-TH` | Tieng Thai | PremwadeeNeural |
| `id-ID` | Tieng Indonesia | GadisNeural |
| `ms-MY` | Tieng Malay | YasminNeural |
| `fil-PH` | Tieng Filipino | BlessicaNeural |

### Chau Au
| Ma | Ngon ngu | Giong edge-tts |
|---|---|---|
| `en-US` | English (My) | AriaNeural |
| `en-GB` | English (Anh) | SoniaNeural |
| `en-AU` | English (Uc) | NatashaNeural |
| `en-CA` | English (Canada) | ClaraNeural |
| `en-IN` | English (An Do) | NeerjaNeural |
| `en-IE` | English (Ireland) | EmilyNeural |
| `en-ZA` | English (Nam Phi) | LeahNeural |
| `en-NZ` | English (New Zealand) | MollyNeural |
| `fr-FR` | Tieng Phap | DeniseNeural |
| `fr-CA` | Phap (Canada) | SylvieNeural |
| `de-DE` | Tieng Duc | KatjaNeural |
| `de-AT` | Duc (Ao) | IngridNeural |
| `it-IT` | Tieng Y | ElsaNeural |
| `es-ES` | Tay Ban Nha (TBN) | ElviraNeural |
| `es-MX` | Tay Ban Nha (Mexico) | DaliaNeural |
| `es-US` | Tay Ban Nha (My) | PalomaNeural |
| `es-AR` | Tay Ban Nha (Argentina) | ElenaNeural |
| `pt-PT` | Tieng Bo Dao Nha | RaquelNeural |
| `pt-BR` | Bo Dao Nha (Brazil) | FranciscaNeural |
| `ru-RU` | Tieng Nga | SvetlanaNeural |
| `nl-NL` | Tieng Ha Lan | ColetteNeural |
| `pl-PL` | Tieng Ba Lan | ZofiaNeural |
| `sv-SE` | Tieng Thuy Dien | SofieNeural |
| `nb-NO` | Tieng Na Uy | PernilleNeural |
| `da-DK` | Tieng Da Mac | ChristelNeural |
| `fi-FI` | Tieng Phan Lan | SelmaNeural |
| `cs-CZ` | Tieng Sec | VlastaNeural |
| `el-GR` | Tieng Hy Lap | AthinaNeural |
| `uk-UA` | Tieng Ukraina | PolinaNeural |
| `ro-RO` | Tieng Romania | AlinaNeural |
| `hu-HU` | Tieng Hung Gia Ri | NoemiNeural |
| `sk-SK` | Tieng Slovakia | ViktoriaNeural |
| `bg-BG` | Tieng Bulgaria | KalinaNeural |
| `hr-HR` | Tieng Croatia | GabrijelaNeural |
| `ca-ES` | Tieng Catalan | JoanaNeural |

### Chau A - Trung Dong
| Ma | Ngon ngu | Giong edge-tts |
|---|---|---|
| `ar-SA` | Tieng A Rap (Saudi) | ZariyahNeural |
| `ar-EG` | A Rap (Ai Cap) | SalmaNeural |
| `ar-AE` | A Rap (UAE) | FatimaNeural |
| `he-IL` | Tieng Hebrew | HilaNeural |
| `tr-TR` | Tieng Tho Nhi Ky | EmelNeural |

## Huong dan su dung

De doi ngon ngu, dung `voice_speak` voi tham so `language`:
- `voice_speak(text="Xin chao", language="vi-VN")` -> Tieng Viet
- `voice_speak(text="Hello", language="en-US")` -> Tieng Anh
- `voice_speak(text="Bonjour", language="fr-FR")` -> Tieng Phap

Sau khi user chon, hay thu bang cach goi `voice_speak` voi mot cau ngan mau trong ngon ngu do.
Nhac ho co the thay doi bat cu luc nao bang lenh `/voice`.
