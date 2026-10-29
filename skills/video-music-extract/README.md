# Video Music Extract

Portable Skill (WorkBuddy, Codex, and any agent that can read `SKILL.md` and run local scripts) that turns a video URL into an mp3, with a single **intent** parameter deciding whether human voice is kept.

## What it does
- `pure` (default) — instrumental only; auto-removes voice with Demucs when a voice is detected, otherwise extracts directly.
- `all` — keeps lead vocals + all dubbing (full track, no separation).
- `chorus` / `C` — keeps choir / "ah" backing vocals (mechanically the full track; Demucs cannot split lead from choir).

Supports Bilibili, YouTube, and any `yt-dlp`-supported site. Multi-P Bilibili via `--page`.

## Requirements
- Python 3.10+
- `ffmpeg` / `ffprobe` on PATH — https://ffmpeg.org/ (macOS: `brew install ffmpeg`; Ubuntu: `apt install ffmpeg`; Windows: `winget install Gyan.FFmpeg`)
- `yt-dlp` on PATH — `pip install yt-dlp` or `pipx install yt-dlp`
- Heavy deps (torch, demucs, onnxruntime, huggingface_hub, numpy) are installed **automatically** into a local venv on first use. YAMNet weights are auto-downloaded from the HuggingFace mirror on first use.

## Install
```bash
python -m pip install -r requirements.txt   # ffmpeg/yt-dlp are system tools, not pip
```

## Quick start
```bash
# Pure music (remove voice if present)
python scripts/extract_music.py \
  --url "https://www.bilibili.com/video/BVxxxx/?p=5" --page 5 \
  --intent pure --out ./output/song.mp3

# Keep vocals + dubbing
python scripts/extract_music.py --url "<URL>" --intent all --out ./output/song.mp3

# Keep choir / "ah" backing
python scripts/extract_music.py --url "<URL>" --intent chorus --out ./output/song.mp3
```

## Environment overrides (all optional)
| Var | Meaning | Default |
|---|---|---|
| `VME_YTDLP` | path to `yt-dlp` | PATH |
| `VME_FFMPEG` / `VME_FFPROBE` | ffmpeg / ffprobe paths | PATH |
| `VME_VENV` | venv dir for torch/demucs/onnxruntime | `<skill>/.cache/venv` (auto-created) |
| `VME_YAMNET_DIR` | dir with `yamnet.onnx` + `yamnet_class_map.csv` | `<skill>/assets` (auto-downloaded) |

## Windows + Chinese output paths (GBK shell caveat)
A legacy Git-Bash shell encodes non-ASCII command-line args as GBK, which a UTF-8 Python mis-decodes into mojibake filenames. Two safe patterns:

1. **Let the script handle it** — it writes to an ASCII temp name then renames inside Python (already built in).
2. **Explicit safe rename** — invoke with an ASCII placeholder, then rename in a UTF-8 `.py` file:
   ```python
   import os
   os.replace(r"./output/_tmp.mp3", r"./output/中文曲名.mp3")
   ```

## License
See the repository `LICENSE`.
