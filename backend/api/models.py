from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    image_filename: str
    audio_filename: str
    style: str = "cinematic"        # cinematic | hype | sad
    engine: str = "wav2lip"         # wav2lip | sadtalker
    lora_model: Optional[str] = None

class JobStatus(BaseModel):
    status: str                     # queued | running | done | failed
    progress: int                   # 0-100
    output: Optional[str] = None    # URL to final MP4
    error: Optional[str] = None
