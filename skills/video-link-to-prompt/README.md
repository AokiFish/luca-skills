# Video Link to Prompt Skill 

Portable Skill for WorkBuddy, Codex, and other agents that can read `SKILL.md` and execute local scripts.

## Included
- `scripts/analyze_video.py`: URL/local-file retrieval, FFprobe metadata, per-second frame extraction, frame-quality scoring, keyframe selection, narrative storyboard planning, optional audio extraction and transcription.
- `scripts/frame_quality.py`: Pillow-only frame metrics (Laplacian-variance sharpness, grayscale contrast, frame-to-frame diff) used to reject black/blurred frames and to find beat boundaries.
- `scripts/vision_api_analyze.py`: optional adapter for an OpenAI-compatible multimodal API.
- `templates/vision-analysis-instructions.md`: how the host agent should inspect extracted frames.
- `templates/master-prompt.md`: reusable prompt template with fixed rules and replaceable variables.

## Requirements
- Python 3.10+
- `python -m pip install -r requirements.txt`
- FFmpeg and FFprobe installed and on PATH: https://ffmpeg.org/
- Optional transcription: `python -m pip install faster-whisper`

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/analyze_video.py --url "https://www.youtube.com/shorts/VIDEO_ID" --out ./video-analysis
```

Local file:

```bash
python scripts/analyze_video.py --file ./reference.mp4 --out ./video-analysis
```

Sampling options:

```bash
python scripts/analyze_video.py --url "VIDEO_URL" --out ./video-analysis --interval 0.5 --max-frames 50
```

Optional transcription (may download a speech model on first run):

```bash
python -m pip install faster-whisper
python scripts/analyze_video.py --url "VIDEO_URL" --out ./video-analysis --transcribe
```

### Keyframes + storyboard (always on)
Keyframes and the storyboard are generated on every run, but **neither is derived from the hard-cut count**:

- **Keyframes (`key_frame/`)** — a keyframe means *the clear state frame that defines the start/end of an action or a change*. Motion-blurred in-between frames are exactly what must NOT be picked, and a hard-cut point sits right at a motion/transition instant. So the script scores every per-second frame (`scripts/frame_quality.py`): it first uses **contrast (grayscale std-dev) to reject black/flat frames**, then takes the **highest-sharpness (Laplacian variance) frame within each storyboard cell** as that cell's representative pose frame (longer cells also get an "opening clear frame"). The manifest records time, cell, role, sharpness, contrast, and how many flat/black candidates were rejected. `--cut-threshold` is **not** used for keyframes.
- **Storyboard (`story_board/`)** — a storyboard is a *narrative / shooting-planning unit*, not a hard-cut counter. Cuts are only one (forced) boundary; cells are also split by **frame-to-frame visual change (beats)**, plus a **max cell length** (`--board-max`, default 5s; over-long cells are bisected, with an equal-time fallback when no change point exists) and a **min cell length** (`--board-min`, default 2s). A one-take sequence is still split into multiple cells. Each cell's representative frame is its clearest informative frame — never the first frame and never the cut frame. Output: `story_board.md` (Obsidian-friendly) + `story_board.html` (one visual card per cell).

```bash
python scripts/analyze_video.py --file ./reference.mp4 --out ./video-analysis --board-max 5 --board-min 2 --board-diff-k 1.5
```

`--cut-threshold` is on a 0–100 scale (percent of frame change); raise it if too many cuts are detected, lower it if fast cuts are missed.

## Host agent workflow
1. Run the extraction script.
2. Read `analysis_bundle.json` and `source_metadata.json`.
3. Inspect the per-second frames under `frames/`, the keyframes under `key_frame/`, and the storyboard under `story_board/` using the host's actual image-understanding tool.
4. Follow `templates/vision-analysis-instructions.md`.
5. Produce the shot table, fixed rules, replaceable variables, and prompt per `SKILL.md`.
6. When writing the report to a file, name it `video-prompt-report-<slug>.md` (slug from the video title / uploader / filename). Never use a bare `video-prompt-report.md`. See `SKILL.md` → "Output file naming".

A text-only host cannot infer what frames depict. In that case, use the optional API adapter if configured or state that semantic visual analysis is unavailable.

## Optional vision API adapter
Only use this if you intentionally want to send frames to an external vision-capable endpoint. Set:
- `OPENAI_API_KEY` (required)
- `VISION_MODEL` (required; must support image inputs at your endpoint)
- `OPENAI_BASE_URL` (optional; defaults to `https://api.openai.com/v1`)

Then:

```bash
python scripts/vision_api_analyze.py --bundle ./video-analysis/analysis_bundle.json --out ./video-analysis/vision_analysis.json
```

Review the provider's privacy, cost and retention terms before sending frames. Do not put keys in Skill files. The adapter reports endpoint/model errors rather than claiming success.

## Output files
- `analysis_bundle.json`: evidence inventory and technical metadata
- `source_metadata.json`: source and retrieval details
- `frames/`: per-second full-resolution frames (the baseline evidence; one frame/sec, uncapped)
- `key_frame/`: **keyframes** — per-cell representative pose frames picked by **sharpness + contrast filtering** (never cut frames), plus `key_frame_manifest.json/.md`
- `story_board/`: **storyboard** — narrative cells (not cut count) with representative frames; `story_board.md` ([待填] annotations: 景别/机位/运动/关键动作/对白音效) and `story_board.html` (visual board, one card per cell)
- `sheets/`: **rhythm/action evidence package** (created automatically)
  - `压缩包_全部帧.jpg`: every per-second frame collapsed into one master image
  - `sheet_XX.jpg`: paginated contact sheets (default 5×9/page) for page-by-page review
  - `_cuts.txt`: scene-cut list + beat stats
  - `节奏实录.md`: per-second anchor skeleton (`[待填]`) to fill with real content
  - `动作模板.md`: blank action-template skeleton to fill with real beats
  - `参考音轨_原片.wav`: extracted reference audio, if available
- `roles/`: **empty by design** — drop adapted-character reference images here (e.g. `主角1.jpg`); a `README.txt` explains the naming
- `audio.wav`: extracted audio, if available
- `transcript.txt` / `transcript.json`: optional transcription
- `access_diagnostic.json`: error details and fallback suggestions
- `vision_analysis.json`: optional API analysis

## Important limits
- A URL may expose metadata but not a downloadable video stream.
- Evenly sampled frames can miss rapid cuts or brief actions.
- FFmpeg/OpenCV-style processing does not equal semantic visual understanding.
- A Skill cannot grant a host new model/tool capabilities.
- Final video alone cannot reveal its original prompt, seed, exact camera/lens, or hidden generation settings.
