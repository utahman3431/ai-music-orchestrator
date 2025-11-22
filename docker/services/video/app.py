import os
from pathlib import Path
from typing import Optional

import imageio
import numpy as np
import torch
from diffusers import StableVideoDiffusionPipeline
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel

MODEL_ID = os.getenv("MODEL_ID", "stabilityai/stable-video-diffusion-img2vid")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

pipe: Optional[StableVideoDiffusionPipeline] = None


class GenerateRequest(BaseModel):
    job_id: str
    init_image_path: Optional[str] = None  # optional path to seed image
    num_frames: int = 14
    fps: int = 7
    seed: Optional[int] = None
    output_dir: Optional[str] = None


app = FastAPI(title="video-gen", version="1.0.0")


@app.on_event("startup")
def _load():
    global pipe
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        use_safetensors=True,
    )
    pipe.to(DEVICE)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID, "device": DEVICE}


@app.post("/generate")
def generate(req: GenerateRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    generator = torch.Generator(device=DEVICE)
    if req.seed is not None:
        generator = generator.manual_seed(req.seed)

    if req.init_image_path:
        init_image = Image.open(req.init_image_path).convert("RGB")
    else:
        init_image = Image.new("RGB", (512, 512), color=(128, 128, 128))

    output_dir = Path(req.output_dir or "/data/orchestration/jobs") / req.job_id / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "video.mp4"

    frames = pipe(
        init_image,
        num_frames=req.num_frames,
        decode_chunk_size=4,
        generator=generator,
    ).frames[0]

    fps = req.fps or 7
    imageio.mimwrite(out_path, [np.array(f) for f in frames], fps=fps)
    return {"status": "completed", "path": str(out_path)}
