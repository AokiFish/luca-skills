# Music Instrument Analysis

Portable Skill (WorkBuddy, Codex, and any agent that can read `SKILL.md` and run local scripts) that identifies the instrument lineup of a music track and explains each instrument's best use-cases and pairings. It uses objective YAMNet (ONNX) instrument probabilities + spectral features + musicology, and can produce a **timeline segmented arrangement table** (which section uses what).

## What it does
- Instrument lineup (YAMNet objective probabilities + AI knowledge correction, layered by confidence)
- Each instrument's role, best use-cases, and best pairings
- `has_voice` flag (is it instrumental?)
- Optional **timeline segmented arrangement** — locate "which section likely uses what" instead of merging the whole track

## Architecture (two layers)
1. **Objective — YAMNet (ONNX, AudioSet 521 classes):** frame-by-frame classification; whole-track max, or per-segment max in timeline mode.
2. **Knowledge — AI:** reads YAMNet output + spectral features (band-energy ratios / centroid / onsets) + genre knowledge for the final call and explanation.

Weights (`yamnet.onnx` + `yamnet_class_map.csv`) live in `assets/` and are **auto-downloaded** from the HuggingFace mirror on first use.

## Requirements
- Python 3.10+
- `ffmpeg` / `ffprobe` on PATH (for `--url` downloads and transcoding)
- `numpy`, `scipy`, `matplotlib`, `onnxruntime` — `pip install -r requirements.txt`
- `yt-dlp` on PATH only if you use `--url` (optional)

## Install
```bash
python -m pip install -r requirements.txt
# optional, for --url:
python -m pip install yt-dlp
```

## Quick start
```bash
# Local file
python scripts/analyze_instruments.py --audio ./song.mp3 \
  --out ./stats.json --png ./spectrogram.png --seg-len 8

# From a video URL (auto-downloaded)
python scripts/analyze_instruments.py --url "https://www.youtube.com/watch?v=ID" \
  --out ./stats.json --png ./spectrogram.png
```

`--seg-len 0` disables segmentation (whole-track only). `--no-yamnet` skips the
objective layer entirely (spectrum-only fallback).

## Environment overrides (all optional)
| Var | Meaning | Default |
|---|---|---|
| `MIA_FFMPEG` / `MIA_FFPROBE` | ffmpeg / ffprobe paths | PATH |
| `MIA_YTDLP` | yt-dlp path | PATH |

## Honest boundaries (read before trusting output)
- YAMNet is an **existence / family-level** classifier, not note-by-note. Reliable: percussion family, voice presence. Unreliable: specific plucked-string names (harp/zheng vs sitar…), and piano is sometimes missed (recovered via spectrum).
- There is **no** "automatically and precisely identify every instrument". Always label confidence + basis. See `SKILL.md` for the full honesty contract.

## License
See the repository `LICENSE`.
