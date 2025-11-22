import os
from pathlib import Path
from typing import Optional

import torch
import torchaudio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoProcessor, MusicgenForConditionalGeneration

MODEL_ID = os.getenv("MODEL_ID", "facebook/musicgen-medium")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

processor: Optional[AutoProcessor] = None
model: Optional[MusicgenForConditionalGeneration] = None


class GenerateRequest(BaseModel):
    job_id: str
    prompt: str
    duration: int = 8
    seed: Optional[int] = None
    output_dir: Optional[str] = None


app = FastAPI(title="audio-gen", version="1.0.0")


@app.on_event("startup")
def _load():
    global processor, model
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = MusicgenForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        use_safetensors=True,
    ).to(DEVICE)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID, "device": DEVICE}


@app.post("/generate")
def generate(req: GenerateRequest):
    if processor is None or model is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    generator = torch.Generator(device=DEVICE)
    if req.seed is not None:
        generator = generator.manual_seed(req.seed)

    inputs = processor(
        text=[req.prompt],
        padding=True,
        return_tensors="pt",
    ).to(DEVICE, model_dtype=DTYPE)

    audio_values = model.generate(
        **inputs,
        do_sample=True,
        guidance_scale=3.0,
        max_new_tokens=req.duration * model.config.audio_encoder_stride,
        pad_token_id=model.generation_config.pad_token_id,
        eos_token_id=model.generation_config.eos_token_id,
        generator=generator,
    )

    output_dir = Path(req.output_dir or "/data/orchestration/jobs") / req.job_id / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "audio.wav"

    audio_np = audio_values[0].cpu().float()
    sample_rate = getattr(getattr(model.config, "audio_encoder", None), "sampling_rate", 32000)
    torchaudio.save(out_path, audio_np, sample_rate=sample_rate)
    return {"status": "completed", "path": str(out_path)}
