# AI Avatar & Reel Generator — Complete Setup Guide

## What This Builds
Upload a face image + audio → get a lip-synced, styled 9:16 MP4 reel.  
Stack: Stable Diffusion · Wav2Lip · SadTalker · FFmpeg · FastAPI · Flutter

---

## Prerequisites

| Requirement     | Notes                                      |
|-----------------|--------------------------------------------|
| NVIDIA GPU      | 6 GB VRAM minimum (8 GB recommended)       |
| CUDA 11.8+      | `nvidia-smi` to check                      |
| Python 3.10+    | `python --version`                         |
| Git             | `git --version`                            |
| FFmpeg          | `ffmpeg -version`                          |
| Flutter 3.x     | For the mobile/web UI                      |

---

## Phase 1 — MVP Setup

### Step 1 — Clone this project
```bash
git clone https://github.com/yourname/ai-avatar-reel.git
cd ai-avatar-reel
```

### Step 2 — Create Python virtual environment
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3 — Install FFmpeg
```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — download from https://ffmpeg.org/download.html and add to PATH
```

### Step 4 — Set up Stable Diffusion (AUTOMATIC1111)
```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui

# Download SDXL model (free, ~6.5 GB)
mkdir -p models/Stable-diffusion
wget -O models/Stable-diffusion/sdxl_base.safetensors \
  https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Launch with API enabled
./webui.sh --api --listen      # macOS/Linux
# webui-user.bat --api --listen  (Windows)
```
> AUTOMATIC1111 will be running at http://localhost:7860
> Leave this terminal open while using the app.

### Step 5 — Set up Wav2Lip
```bash
cd ..  # back to project root
mkdir -p models && cd models
git clone https://github.com/Rudrabha/Wav2Lip
cd Wav2Lip

pip install -r requirements.txt

# Download checkpoints (required)
mkdir checkpoints
# wav2lip_gan.pth — best quality
wget -O checkpoints/wav2lip_gan.pth \
  "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUF0MDkBjqkpEZkU5jvCDGRs1xhfHw"

# face detection model
wget -O face_detection/detection/sfd/s3fd.pth \
  "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth"
```

### Step 6 — Start the FastAPI backend
```bash
cd /path/to/ai-avatar-reel
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```
> API now running at http://localhost:8000
> Interactive docs at http://localhost:8000/docs

### Step 7 — Test the pipeline (API)
```bash
# Upload a face image
curl -X POST http://localhost:8000/api/upload/image \
  -F "file=@your_face.jpg"
# → {"filename": "abc123.jpg"}

# Upload audio
curl -X POST http://localhost:8000/api/upload/audio \
  -F "file=@your_song.mp3"
# → {"filename": "def456.mp3"}

# Generate reel
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"image_filename":"abc123.jpg","audio_filename":"def456.mp3","style":"cinematic","engine":"wav2lip"}'
# → {"job_id": "xyz-789"}

# Poll status
curl http://localhost:8000/api/job/xyz-789
# → {"status":"done","progress":100,"output":"/outputs/xyz-789_final.mp4"}
```

---

## Phase 2 — SadTalker + Flutter UI

### Step 8 — Set up SadTalker
```bash
cd models
git clone https://github.com/OpenTalker/SadTalker
cd SadTalker
pip install -r requirements.txt

# Download checkpoints (auto script)
bash scripts/download_models.sh
```

### Step 9 — Run Flutter UI
```bash
cd frontend

# Install Flutter: https://docs.flutter.dev/get-started/install
flutter pub get

# Run on web
flutter run -d chrome

# Run on Android (connect device or start emulator)
flutter run -d android
```
> The Flutter app connects to http://localhost:8000 by default.
> Change `baseUrl` in `lib/services/api_service.dart` for remote deployments.

---

## Phase 3 — LoRA Training for Avatar Consistency

### Step 10 — Prepare your character dataset
1. Generate 20–50 face images using Stable Diffusion (via the API or A1111 UI).
2. Curate — keep only clean, varied shots (different angles, lighting).
3. Save them to `data/my_character/`.

### Step 11 — Install kohya-ss
```bash
cd models
git clone https://github.com/bmaltais/kohya_ss
cd kohya_ss
pip install -r requirements.txt
```

### Step 12 — Train LoRA
```bash
cd /path/to/ai-avatar-reel
python scripts/train_lora.py \
  --images_dir data/my_character \
  --output_name my_char_v1 \
  --caption "mycharacter" \
  --steps 1500
```
> Training takes 20–60 min on a GPU.
> Output saved to `models/loras/my_char_v1.safetensors`.

### Step 13 — Use LoRA in generation
Copy the `.safetensors` file to AUTOMATIC1111's `models/Lora/` folder.
When calling the API, pass `"lora_model": "my_char_v1"` in your generate request.

---

## Phase 2 Smart Features — Beat Cuts

### Beat-synced video
```bash
pip install librosa
python scripts/beat_cuts.py \
  --audio my_song.mp3 \
  --video animated.mp4 \
  --output beat_reel.mp4
```

---

## Deployment Options

### Local (recommended for GPU)
```bash
# Everything runs on your machine — no cost, full GPU access
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Docker (GPU passthrough)
```bash
docker compose up --build
```

### Google Colab (free testing, no persistent GPU)
1. Upload the project to Google Drive.
2. Mount Drive in Colab.
3. Run `!pip install -r requirements.txt` in a cell.
4. Use `!uvicorn backend.main:app &` then use ngrok for public URL.

---

## Directory Structure
```
ai-avatar-reel/
├── backend/
│   ├── main.py               ← FastAPI app
│   ├── api/models.py         ← Pydantic schemas
│   └── pipeline/
│       ├── sd_generator.py   ← Stable Diffusion
│       ├── animator.py       ← Wav2Lip / SadTalker
│       ├── video_processor.py← FFmpeg
│       └── generator.py      ← Pipeline orchestrator
├── frontend/                 ← Flutter app
│   └── lib/
│       ├── main.dart
│       ├── screens/
│       └── services/
├── scripts/
│   ├── train_lora.py         ← LoRA training
│   └── beat_cuts.py          ← Beat detection
├── models/                   ← Clone Wav2Lip, SadTalker, kohya here
├── storage/
│   ├── uploads/
│   └── outputs/
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `CUDA out of memory` | Reduce image size to 256×256, use `--resize_factor 2` in Wav2Lip |
| `Wav2Lip: face not detected` | Use a clear frontal face image, min 256px |
| `A1111 API not responding` | Make sure webui is running with `--api` flag |
| `FFmpeg not found` | Check PATH: `which ffmpeg` |
| `SadTalker: model files missing` | Re-run `bash scripts/download_models.sh` |
| Flutter `connection refused` | Check backend is running on port 8000 |

---

## License
All tools used are open-source. Do not use real person images. Ensure your audio has appropriate rights for use.
