---
name: video-music-extract
description: Extract music as mp3 from any video URL (Bilibili, YouTube, and any yt-dlp-supported site). A single "intent" parameter controls whether voice is kept: pure (default, auto-remove voice), all (keep lead vocals + all dubbing), chorus/C (keep choir/"ah" backing vocals). Trigger when the user says "extract music / pure music / remove vocals / instrumental only / keep the vocals / keep the chorus / pull the BGM".
version: "1.0.0"
agent_created: true
triggers:
  - 提炼音乐
  - 提取纯音乐
  - 去人声
  - 只要伴奏
  - 把背景音乐弄出来
  - 分离人声
  - 含人声配音
  - 保留合唱
  - extract music
  - remove vocals
  - instrumental only
---

# Video → Music (Video Music Extract)

## What it does
Turn the audio of a video into a 44.1 kHz / 256 kbps mp3, with a single **intent**
parameter deciding **whether human voice is kept**. Works with Bilibili, YouTube,
and any site supported by `yt-dlp`. Multi-P Bilibili videos are supported via `--page`.

## Intent parameter (the one knob — never ask back)
| Intent | Keywords | Behavior |
|---|---|---|
| `pure` (default, no arg) | "纯音乐", "去人声", "只要伴奏", "分离人声", no special instruction | Output has **no voice**. Only runs Demucs separation (`no_vocals`) when YAMNet detects voice; if the source is already instrumental it is extracted directly (faster, no artifacts). |
| `all` | "all", "含人声", "含原唱", "含配音", "keep vocals + dubbing" | Extract the **full track** — keeps lead vocals + all dubbing, no separation. |
| `chorus` / `C` | "C", "合唱", "保留合唱", "keep choir", "ah" backing only | Extract the full track, keeping choir/"ah" backing vocals. |

**Honest boundary:** Demucs can only split *all* voice from accompaniment — it
cannot isolate "lead" from "choir". So `chorus` and `all` are mechanically the
same (full track). If the source also has real lead lyrics, `chorus` keeps those
too; truly "choir-only, no lead" would need a lead/backing model not wired in here.

## When to use
- "extract the pure music from this video" → pure
- "remove vocals, instrumental only" → pure
- "keep the original vocals and dubbing, whole song" → all
- "keep the chorus (C)" → chorus
- "make this Bilibili p=5 song an mp3" → no instruction → pure

## Workflow

### 1. Parse the request
Extract: video URL, target name (use the song/video title; Chinese is fine), Bilibili
page index (`p=N` in URL), and **intent** (from the table; default pure).

### 2. Run the helper script
Script: `scripts/extract_music.py`. All external calls use subprocess list args,
so Unicode paths are shell-safe.

```bash
# Run with whatever python has onnxruntime (for pure-intent voice detection);
# the script auto-creates a venv with torch/demucs/onnxruntime if needed.
python "$SKILL/scripts/extract_music.py" \
  --url "https://www.bilibili.com/video/BVxxxx/?p=5" \
  --page 5 \
  --intent pure \            # pure(default) | all | chorus
  --out "/path/to/曲名.mp3"
```
- `--page` only for multi-P Bilibili; omit for single videos.
- `--intent`: `pure` (default) / `all` / `chorus`. The script auto-decides the
  underlying `extract` vs `separate` (`pure` separates only when voice is detected).
- `--mode extract|separate` overrides the underlying action explicitly (advanced).
- `--out` target mp3 path (may contain Chinese).
- Script prints `[intent=...] voice detection: has_voice=...`,
  `[decision] intent=... -> mode=...`, `DONE: <abs path>` and `INFO:` (duration/codec).
  Use those to deliver to the user.

### 3. Deliver
After confirming `INFO` shows `codec_name=mp3` and a sane `duration`, present the
mp3 file to the user.

## Configuration (env vars, all optional)
The script auto-discovers tools on PATH. Override only if needed:
- `VME_YTDLP`  — path to `yt-dlp` (default: PATH)
- `VME_FFMPEG` / `VME_FFPROBE` — paths to `ffmpeg` / `ffprobe` (default: PATH)
- `VME_VENV`   — venv dir for torch/demucs/onnxruntime (default: `<skill>/.cache/venv`, auto-created)
- `VME_YAMNET_DIR` — dir holding `yamnet.onnx` + `yamnet_class_map.csv` (default: `<skill>/assets`, auto-downloaded)

## Pitfalls & notes
- **Windows legacy Git-Bash + Chinese paths:** never pass a non-ASCII `--out`
  directly through a GBK-encoded shell — it mojibakes. Two safe options:
  1. Let the script handle it (it writes via an ASCII temp then renames), or
  2. use an ASCII temp name and rename in a `.py` file (UTF-8 source) afterward.
  See `README.md` for a safe-invocation snippet.
- **Bilibili HD:** `1080P high-bitrate` needs premium; `bestaudio` (free) is enough.
- **Login-limited sites:** if yt-dlp complains, add `--cookies-from-browser`.
- **Copyright:** personal listening only; do not re-upload or commercialize.

## One-time Demucs install (handled automatically)
First `separate` run auto-creates a venv and installs CPU torch + demucs +
onnxruntime + numpy + huggingface_hub. If auto-install fails (e.g. pytorch.org
unreachable), do it manually with the env override:
```bash
python -m venv /path/to/venv
/path/to/venv/Scripts/python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
/path/to/venv/Scripts/python -m pip install demucs onnxruntime numpy huggingface_hub
# then: VME_VENV=/path/to/venv python scripts/extract_music.py ...
```
- **Time:** CPU separation of a ~4 min track takes 5–10 min. Prefer background execution.
- **Model download:** Demucs pulls its model from HuggingFace on first run; if
  `huggingface.co` times out, the script auto-retries via `https://hf-mirror.com`.
