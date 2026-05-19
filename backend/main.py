"""
AI Avatar & Reel Generator — FastAPI Backend
"""
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid, os, shutil
from pathlib import Path
from backend.pipeline.generator import run_pipeline
from backend.api.models import JobStatus, GenerateRequest

app = FastAPI(title="AI Avatar Reel Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("storage/uploads")
OUTPUT_DIR = Path("storage/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/outputs", StaticFiles(directory="storage/outputs"), name="outputs")

jobs: dict[str, dict] = {}


@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": filename, "path": str(path)}


@app.post("/api/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": filename, "path": str(path)}


@app.post("/api/generate")
async def generate_reel(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "progress": 0, "output": None, "error": None}
    background_tasks.add_task(run_pipeline, job_id, req, jobs, OUTPUT_DIR)
    return {"job_id": job_id}


@app.get("/api/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/api/health")
async def health():
    return {"status": "ok"}
