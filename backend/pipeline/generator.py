"""
Pipeline orchestrator — called by FastAPI background task.
Runs: face_image → animate → ffmpeg → final MP4
"""
import uuid
from pathlib import Path
from backend.api.models import GenerateRequest
from backend.pipeline.animator import animate
from backend.pipeline.video_processor import process_video

UPLOAD_DIR = Path("storage/uploads")


def run_pipeline(
    job_id: str,
    req: GenerateRequest,
    jobs: dict,
    output_dir: Path,
):
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["progress"] = 10

        face_path  = UPLOAD_DIR / req.image_filename
        audio_path = UPLOAD_DIR / req.audio_filename

        if not face_path.exists():
            raise FileNotFoundError(f"Face image not found: {face_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Step 1 — Animate (lip-sync)
        jobs[job_id]["progress"] = 30
        animated_path = output_dir / f"{job_id}_animated.mp4"
        animate(face_path, audio_path, animated_path, engine=req.engine, style=req.style)

        # Step 2 — Video processing (9:16 crop + style)
        jobs[job_id]["progress"] = 70
        final_path = output_dir / f"{job_id}_final.mp4"
        process_video(animated_path, audio_path, final_path, style=req.style)

        # Done
        jobs[job_id]["status"]   = "done"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["output"]   = f"/outputs/{final_path.name}"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"]  = str(e)
