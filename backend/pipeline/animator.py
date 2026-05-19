"""
Lip-sync animation using Wav2Lip or SadTalker.

Prerequisites:
  Wav2Lip:   git clone https://github.com/Rudrabha/Wav2Lip  (place in /models/Wav2Lip)
  SadTalker: git clone https://github.com/OpenTalker/SadTalker (place in /models/SadTalker)
"""
import subprocess, shutil
from pathlib import Path

WAV2LIP_DIR   = Path("models/Wav2Lip")
SADTALKER_DIR = Path("models/SadTalker")
WAV2LIP_CKPT  = WAV2LIP_DIR / "checkpoints/wav2lip_gan.pth"


def run_wav2lip(face_path: Path, audio_path: Path, output_path: Path) -> Path:
    """
    Run Wav2Lip inference.
    Returns path to the output video.
    """
    cmd = [
        "python", str(WAV2LIP_DIR / "inference.py"),
        "--checkpoint_path", str(WAV2LIP_CKPT),
        "--face",            str(face_path),
        "--audio",           str(audio_path),
        "--outfile",         str(output_path),
        "--resize_factor",   "1",
        "--nosmooth",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Wav2Lip failed:\n{result.stderr}")
    return output_path


def run_sadtalker(face_path: Path, audio_path: Path, output_dir: Path,
                  expression: str = "default") -> Path:
    """
    Run SadTalker inference.
    expression: default | sad | happy | angry
    Returns path to the output video.
    """
    cmd = [
        "python", str(SADTALKER_DIR / "inference.py"),
        "--driven_audio",   str(audio_path),
        "--source_image",   str(face_path),
        "--result_dir",     str(output_dir),
        "--still",
        "--preprocess",     "crop",
        "--expression_scale", "1.2" if expression != "default" else "1.0",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"SadTalker failed:\n{result.stderr}")

    # SadTalker writes its own filename; find the newest .mp4
    videos = sorted(output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    if not videos:
        raise FileNotFoundError("SadTalker produced no output video")
    return videos[-1]


def animate(face_path: Path, audio_path: Path, output_path: Path,
            engine: str = "wav2lip", style: str = "cinematic") -> Path:
    """Unified entry-point: picks engine and returns final animated video path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if engine == "sadtalker":
        return run_sadtalker(face_path, audio_path, output_path.parent, expression=style)
    return run_wav2lip(face_path, audio_path, output_path)
