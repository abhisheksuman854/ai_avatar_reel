"""
Image generation via Stable Diffusion (AUTOMATIC1111 REST API)
Make sure AUTOMATIC1111 is running with --api flag:
    python webui.py --api --listen
"""
import requests, base64, uuid
from pathlib import Path

A1111_URL = "http://127.0.0.1:7860"

STYLE_PROMPTS = {
    "cinematic": "cinematic lighting, shallow depth of field, film grain, professional portrait",
    "hype":      "vibrant neon colors, high energy, dramatic contrast, urban aesthetic",
    "sad":       "muted tones, overcast lighting, melancholic mood, soft shadows",
}

NEGATIVE_PROMPT = (
    "blurry, bad anatomy, extra limbs, poorly drawn face, mutation, "
    "deformed, watermark, text, logo, real person, photograph"
)


def generate_avatar(
    prompt: str,
    style: str = "cinematic",
    output_dir: Path = Path("storage/outputs"),
    lora_model: str | None = None,
    seed: int = -1,
    width: int = 512,
    height: int = 512,
) -> Path:
    """
    Generate a synthetic avatar face via AUTOMATIC1111 API.
    Returns the saved image path.
    """
    style_suffix = STYLE_PROMPTS.get(style, "")
    full_prompt = f"{prompt}, {style_suffix}"
    if lora_model:
        full_prompt += f" <lora:{lora_model}:0.8>"

    payload = {
        "prompt": full_prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 30,
        "cfg_scale": 7,
        "width": width,
        "height": height,
        "seed": seed,
        "sampler_name": "DPM++ 2M Karras",
    }

    resp = requests.post(f"{A1111_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    img_data = base64.b64decode(data["images"][0])
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"avatar_{uuid.uuid4().hex[:8]}.png"
    out_path.write_bytes(img_data)
    return out_path


def batch_generate(prompt: str, count: int = 4, style: str = "cinematic",
                   output_dir: Path = Path("storage/outputs")) -> list[Path]:
    """Generate multiple variations for LoRA dataset preparation."""
    return [generate_avatar(prompt, style=style, output_dir=output_dir) for _ in range(count)]
