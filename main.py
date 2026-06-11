import edge_tts
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
import os

app = FastAPI(title="Zabon TTS Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

VOICES = {
    "en": "en-US-AriaNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "tr": "tr-TR-EmelNeural",
    "ar": "ar-SA-ZariyahNeural",
}


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    lang: str | None = "en"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tts")
async def generate_tts(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    voice = req.voice or VOICES.get(req.lang, "en-US-AriaNeural")

    try:
        communicate = edge_tts.Communicate(req.text, voice)
        audio_chunks: list[bytes] = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        if not audio_chunks:
            raise HTTPException(status_code=500, detail="TTS produced no audio")

        audio_data = b"".join(audio_chunks)

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=tts.mp3",
                "X-Audio-Size": str(len(audio_data)),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
