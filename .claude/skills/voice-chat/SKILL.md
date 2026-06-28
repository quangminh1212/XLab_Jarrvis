---
name: voice-chat
description: Vao che do tro chuyen bang giong noi lien tuc (always-on voice)
user_invocable: true
---

Vao che do tro chuyen bang giong noi. Agent se luon lang nghe, cho user noi, hieu y roi tra loi bang giong noi, roi lai tiep tuc nghe.

Quy trinh lap lai mai cho den khi user noi "thoi", "dung lai", "ket thuc", "tam biet", hoac viet van ban yeu cau dung.

Vong lap:
1. Goi `voice_wait_for_speech` de lang nghe. Tool nay se block cho den khi user bat dau noi va dung lai.
2. Nhan duoc van ban, phan tich y cua user.
3. Tra loi tu nhien (toi da 2-3 cau). Neu can, dung `voice_speak` de noi tra loi.
4. Quay lai buoc 1.

Luu y:
- Neu user chi noi nham hoac khong ro, dung `voice_speak("Toi nghe chua ro, ban noi lai duoc khong?")` roi nghe tiep.
- Neu user noi "tam biet" / "bye" / "thoi", tra loi tam biet bang giong noi roi dung vong lap.
- Neu can giai thich dai, nen chia thanh tung cau ngan va noi tung cau bang `voice_speak`.
- Ho tro da ngon ngu: neu user noi tieng Viet thi tra loi tieng Viet, noi tieng Anh thi tra loi tieng Anh.
