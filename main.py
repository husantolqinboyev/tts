import edge_tts
import asyncio
import tempfile
import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Zabon TTS Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

VOICES = {
    "en": "en-US-GuyNeural",
    "ru": "ru-RU-DmitryNeural",
    "tr": "tr-TR-AhmetNeural",
    "ar": "ar-SA-HamedNeural",
}


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    lang: str | None = "en"


@app.get("/")
async def root():
    return {"service": "zabon-tts", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tts")
async def generate_tts(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    voice = req.voice or VOICES.get(req.lang, "en-US-AriaNeural")

    tmp_path = None
    try:
        communicate = edge_tts.Communicate(req.text.strip(), voice)

        tmp_path = tempfile.mktemp(suffix=".mp3")
        await communicate.save(tmp_path)

        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            raise HTTPException(status_code=500, detail="TTS produced no audio")

        with open(tmp_path, "rb") as f:
            audio_data = f.read()

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=tts.mp3",
                "X-Audio-Size": str(len(audio_data)),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print(f"TTS ERROR: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
