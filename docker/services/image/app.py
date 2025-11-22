import os
from pathlib import Path
from typing import Optional

import torch
from diffusers import StableDiffusionPipeline
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_ID = os.getenv("MODEL_ID", "runwayml/stable-diffusion-v1-5")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

pipe: Optional[StableDiffusionPipeline] = None


class GenerateRequest(BaseModel):
    job_id: str
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: int = 25
    guidance_scale: float = 7.0
    height: int = 512
    width: int = 512
    seed: Optional[int] = None
    output_dir: Optional[str] = None


app = FastAPI(title="image-gen", version="1.0.0")


@app.on_event("startup")
def _load():
    global pipe
    pipe = StableDiffusionPipeline.from_pretrained(
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

    output_dir = Path(req.output_dir or "/data/orchestration/jobs") / req.job_id / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "image.png"

    images = pipe(
        req.prompt,
        negative_prompt=req.negative_prompt,
        num_inference_steps=req.num_inference_steps,
        guidance_scale=req.guidance_scale,
        height=req.height,
        width=req.width,
        generator=generator,
    ).images

    images[0].save(out_path)
    return {"status": "completed", "path": str(out_path)}
