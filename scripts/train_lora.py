"""
LoRA Training Helper — prepares dataset and launches kohya-ss training.

Prerequisites:
  git clone https://github.com/bmaltais/kohya_ss  (place at /models/kohya_ss)
  pip install -r models/kohya_ss/requirements.txt

Usage:
  python scripts/train_lora.py --images_dir data/my_character --output_name my_char_v1
"""
import argparse, subprocess, shutil
from pathlib import Path
from PIL import Image

KOHYA_DIR    = Path("models/kohya_ss")
TRAIN_SCRIPT = KOHYA_DIR / "train_network.py"
BASE_MODEL   = "runwayml/stable-diffusion-v1-5"   # swap for SDXL as needed


def prepare_dataset(images_dir: Path, output_dir: Path, caption: str, repeats: int = 20):
    """
    Copy images into kohya repeats folder and write .txt caption files.
    Folder name format:  {repeats}_{caption_token}
    """
    folder = output_dir / f"{repeats}_{caption.replace(' ', '_')}"
    folder.mkdir(parents=True, exist_ok=True)

    for img_path in images_dir.glob("*.[jp][pn][g]*"):
        dest = folder / img_path.name
        shutil.copy(img_path, dest)
        # Write caption (trigger word + descriptors)
        (folder / img_path.stem).with_suffix(".txt").write_text(
            f"{caption}, synthetic avatar, digital art"
        )
    print(f"Dataset ready: {folder}  ({len(list(folder.glob('*.png')))} images)")
    return folder


def train_lora(
    dataset_dir: Path,
    output_name: str,
    output_dir: Path = Path("models/loras"),
    steps: int = 1500,
    lr: float = 1e-4,
    rank: int = 16,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python", str(TRAIN_SCRIPT),
        "--pretrained_model_name_or_path", BASE_MODEL,
        "--train_data_dir",                str(dataset_dir.parent),
        "--output_dir",                    str(output_dir),
        "--output_name",                   output_name,
        "--max_train_steps",               str(steps),
        "--learning_rate",                 str(lr),
        "--network_dim",                   str(rank),
        "--network_alpha",                 str(rank // 2),
        "--save_model_as",                 "safetensors",
        "--mixed_precision",               "fp16",
        "--xformers",
        "--gradient_checkpointing",
        "--resolution",                    "512,512",
        "--train_batch_size",              "1",
        "--lr_scheduler",                  "cosine_with_restarts",
    ]
    print("Starting LoRA training …")
    result = subprocess.run(cmd, timeout=7200)
    if result.returncode != 0:
        raise RuntimeError("LoRA training failed — check output above")
    print(f"LoRA saved → {output_dir / output_name}.safetensors")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir",   required=True)
    parser.add_argument("--output_name",  required=True)
    parser.add_argument("--caption",      default="mycharacter")
    parser.add_argument("--steps",        type=int, default=1500)
    args = parser.parse_args()

    images_dir  = Path(args.images_dir)
    dataset_dir = Path("data/dataset")
    ds = prepare_dataset(images_dir, dataset_dir, args.caption)
    train_lora(ds, args.output_name, steps=args.steps)
