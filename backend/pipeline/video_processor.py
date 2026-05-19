"""
FFmpeg video post-processing: crop to 9:16, add effects, sync audio.
FFmpeg must be installed: sudo apt install ffmpeg
"""
import subprocess
from pathlib import Path

STYLE_FILTERS = {
    "cinematic": "eq=contrast=1.1:saturation=0.85,vignette=PI/4",
    "hype":      "eq=contrast=1.3:saturation=1.6:brightness=0.05,unsharp=5:5:0.8",
    "sad":       "eq=contrast=0.95:saturation=0.4,hue=s=0.3",
}


def process_video(
    input_path: Path,
    audio_path: Path,
    output_path: Path,
    style: str = "cinematic",
    target_w: int = 1080,
    target_h: int = 1920,
) -> Path:
    """
    Crop, style, and audio-sync a video for 9:16 reels.
    Returns the final output path.
    """
    vf = _build_vf(style, target_w, target_h)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-i", str(audio_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr}")
    return output_path


def _build_vf(style: str, w: int, h: int) -> str:
    """Build the FFmpeg -vf filter chain."""
    scale_crop = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h}"
    )
    style_filter = STYLE_FILTERS.get(style, "")
    parts = [scale_crop]
    if style_filter:
        parts.append(style_filter)
    return ",".join(parts)


def add_subtitles(video_path: Path, srt_path: Path, output_path: Path) -> Path:
    """Burn subtitles into the video (Phase 2)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        raise RuntimeError(f"Subtitle burn failed:\n{result.stderr}")
    return output_path
