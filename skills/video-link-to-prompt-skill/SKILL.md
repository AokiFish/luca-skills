---
name: video-link-to-prompt
description: Analyze a video URL or local video, automatically retrieve accessible media, extract keyframes and audio evidence, use the host agent's existing multimodal capability or an optional configured vision API, and produce a grounded shot breakdown plus reusable cross-model video prompts.
version: "0.01.0"
---

# Video Link → Evidence → Shot Breakdown → Reusable Prompt

## Purpose
Turn a reference video into a practical creative blueprint and an original adaptable prompt. Separate **observed evidence**, **interpretation**, and **unknowns**. Also separate **fixed production rules** from **replaceable variables**.

## Core architecture: host agent first
This Skill does **not** require a separate local vision model by default.

1. Run `scripts/analyze_video.py` to retrieve accessible media and extract timestamped frames/audio.
2. Inspect the contact sheet and individual frames using the **actual image/multimodal capability available in the current host agent** (WorkBuddy, Codex, or another host).
3. If the host can inspect images but not video, reason over timestamped frames in order and state that motion interpretation is frame-based, not continuous playback.
4. If host-native visual inspection is unavailable, the optional `scripts/vision_api_analyze.py` can call a configured OpenAI-compatible vision endpoint.
5. If neither route is available, return the technical evidence report and explicitly state that semantic visual analysis could not be completed. Never invent scene descriptions.

**A Skill cannot grant tools the host does not expose.** Do not claim a host-native vision call happened unless it actually did.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/analyze_video.py --url "https://www.youtube.com/shorts/VIDEO_ID" --out ./video-analysis
```

Local file:

```bash
python scripts/analyze_video.py --file ./reference.mp4 --out ./video-analysis
```

Optional transcription:

```bash
python -m pip install faster-whisper
python scripts/analyze_video.py --url "VIDEO_URL" --out ./video-analysis --transcribe
```

The script uses `yt-dlp` for URL retrieval, FFprobe for metadata, FFmpeg for frame/audio extraction, and Pillow for the contact sheet. It **does not understand the meaning** of frames.

## Retrieval fallback ladder
1. Run the script on the supplied URL/file before asking the user to upload anything.
2. If download fails, update `yt-dlp` and retry once only.
3. If available, inspect the page with a permitted browser/connector for video/captions.
4. Treat thumbnails and page metadata as metadata only, never as proof of the full video.
5. Captions/transcripts support dialogue and approximate timing only; they do not prove visuals.
6. If media remains inaccessible, report the exact limitation and ask for one simple fallback: an accessible direct media URL, local video file, or keyframes plus transcript. Never bypass DRM, private/login-only access, paywalls, or access controls.

## Workflow

### 1. Intake and evidence inventory
Record whether full video, sampled frames, audio, transcript, thumbnail/page metadata, or only technical metadata were available. Read `analysis_bundle.json`, `source_metadata.json`, and `access_diagnostic.json` if present. Inspect actual frame images; their existence is not proof they were visually inspected.

### 2. Analyze only what evidence supports
- **Hook and premise:** opening attention grabber, core idea, audience.
- **Narrative beats:** setup → development → escalation → payoff/ending, only where present.
- **Visual system:** subject, environment, props, wardrobe, composition, palette.
- **Shot language:** framing, shot size, angle, subject placement, apparent camera movement, focus cues.
- **Action and timing:** visible verbs, start/middle/end state, pauses and reactions.
- **Lighting/color:** apparent direction, softness, contrast, exposure and palette; do not invent gear or numeric settings.
- **Sound:** dialogue, ambience, effects, music and sync only if audio/transcript supports it.
- **Editing/continuity:** shot changes, movement direction, eyelines, props/wardrobe, transitions.
- **Transferable method:** explain likely creative purpose and generalize it without copying distinctive expression.
- **Improvement ideas:** label as suggestions, not observations.

### 3. Shot table
For each confidently distinguishable shot/beat include shot number, approximate time range, evidence/confidence, shot size/angle, subject/setting, primary action, camera/framing, lighting/color, audio/dialogue, transition/continuity, and narrative function. Sparse sampled frames may miss cuts and brief actions; label boundaries approximate and do not invent precise timecodes.

### 4. Fixed rules vs replaceable variables
**Fixed rules** are transferable production constraints, for example: readable opening hook; one primary action per shot; visible start/middle/end for important movement; consistent subject/wardrobe/props/location; camera motion serves action; coherent lighting; enough time for the payoff. Keep only rules supported by the reference or clearly labeled as improvements.

**Replaceable variables** should be explicit fields, e.g. `[MAIN SUBJECT]`, `[SETTING]`, `[GOAL]`, `[OBSTACLE]`, `[KEY PROP]`, `[ESCALATION]`, `[PAYOFF]`, `[VISUAL STYLE]`, `[COLOR PALETTE]`, `[SOUND DESIGN]`, `[TARGET DURATION]`, `[ASPECT RATIO]`, `[TARGET MODEL]`. Do not mistake a reference's exact character, story, dialogue, or location for a fixed rule.

### 5. Generate and adapt prompt
Use `templates/master-prompt.md`. Fill known fields. For a ready-to-run prompt, do not leave placeholders unless the user asks for a template. Use observable, temporally coherent actions. Label each shot in multi-shot work and state continuity anchors. Keep creative prompt separate from model parameters. Only claim support for features/settings verified for the target model/version. Do not assume every model supports audio, negative prompts, reference images, fixed seeds, multi-shot generation, or identical duration/aspect controls.

### 6. Quality check
- Shot claims grounded in evidence; observation/inference/unknown separated.
- Timestamps appropriately approximate.
- Each shot has a clear action and temporal progression.
- Camera motion and action are compatible.
- Subject, wardrobe, props and location continuity are explicit.
- Payoff is readable and timed.
- Audio instructions supported by audio evidence.
- Fixed rules separated from variables.
- Model parameters separated from prompt prose.
- Output is ready to use without requiring the user to learn the method.

## Default output structure
1. Access/evidence status
2. Creative summary: premise, hook, beats, payoff
3. Shot-by-shot breakdown table
4. Why it works (interpretation)
5. Fixed rules vs replaceable variables
6. Ready-to-use prompt
7. Supported model settings, if known
8. Two to four risks/next-iteration checks

When asked only to build or modify a Skill, provide the artifact rather than applying the workflow.

## Copyright and honesty
Do not imply the user owns the reference. Transfer high-level techniques while changing distinctive characters, dialogue and scene expression. Do not reproduce long copyrighted dialogue/lyrics. Never invent source access, timestamps, model settings, camera metadata, original prompts or seeds.
