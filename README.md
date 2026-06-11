# Zabon TTS Service

Zabon AI uchun Edge TTS backend. Python FastAPI + edge-tts kutubxonasi asosida.

## API

### `POST /tts`
Matnni Edge TTS orqali MP3 audio ga aylantiradi.

**Request:**
```json
{
  "text": "Hello, how are you?",
  "lang": "en",
  "voice": "en-US-AriaNeural"
}
```

**Response:** `audio/mpeg` (MP3 fayl)

**Qo'llab-quvvatlanadigan tillar:**
- `en` — English (en-US-AriaNeural)
- `ru` — Русский (ru-RU-SvetlanaNeural)
- `tr` — Türkçe (tr-TR-EmelNeural)
- `ar` — العربية (ar-SA-ZariyahNeural)

### `GET /health`
Service holatini tekshiradi.

## Deploy

### Render (rekomendatsiya)
1. GitHub'ga push qiling
2. Render'da New → Web Service → Docker
3. Dockerfile: `./Dockerfile`
4. Plan: Free
5. Deploy

### Local ishga tushirish
```bash
pip install -r requirements.txt
python main.py
```

## Environment
- `PORT` — server porti (default: 8000)
