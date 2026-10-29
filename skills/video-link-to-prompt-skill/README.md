# Video Link to Prompt Skill 

Portable Skill for WorkBuddy, Codex, and other agents that can read `SKILL.md` and execute local scripts.

## Included
- `scripts/analyze_video.py`: URL/local-file retrieval, FFprobe metadata, timestamped frame extraction, contact sheet, optional audio extraction and transcription.
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

## Host agent workflow
1. Run the extraction script.
2. Read `analysis_bundle.json` and `source_metadata.json`.
3. Inspect `contact_sheet.jpg` and timestamped images under `frames/` using the host's actual image-understanding tool.
4. Follow `templates/vision-analysis-instructions.md`.
5. Produce the shot table, fixed rules, replaceable variables, and prompt per `SKILL.md`.
6. When writing the report to a file, name it `video-prompt-report_<slug>.md` (slug from the video title / uploader / filename). Never use a bare `video-prompt-report.md`. See `SKILL.md` → "Output file naming".

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
- `frames/`: timestamped keyframes
- `contact_sheet.jpg`: overview of sampled frames
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
