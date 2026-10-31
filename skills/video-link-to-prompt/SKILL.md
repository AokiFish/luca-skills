---
name: video-link-to-prompt
description: Analyze a video URL or local video, automatically retrieve accessible media, extract keyframes and audio evidence, use the host agent's existing multimodal capability or an optional configured vision API, and produce a grounded shot breakdown plus reusable cross-model video prompts. Output reaches shot-level detail: ordered action beats, camera position/movement, shot size, sound, per-segment color tone, and end-frame anchors — so the breakdown can be reused with any new character produced by image-reference-to-prompt.
version: "0.02.0"
---

# Video Link → Evidence → Shot Breakdown → Reusable Prompt

## Purpose
Turn a reference video into a practical creative blueprint and an original adaptable prompt. Separate **observed evidence**, **interpretation**, and **unknowns**. Also separate **fixed production rules** from **replaceable variables**.

The report must be **shot-level detailed enough to regenerate the video beat-by-beat with a different character set**: for every shot/unit it records the ordered **action beats (动作模板)**, the **camera position and movement (机位运动)**, the **shot size (景别)**, the **sound**, the **segment color tone**, and the **end-frame anchor**. Characters are kept as **placeholders** so the same breakdown can be re-run with new characters from `image-reference-to-prompt`.

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

### Sampling strategy (this decides report fidelity)
- **Default = per-second, full-coverage (逐秒逐帧解析)**: the script samples **one frame per second across the whole clip, uncapped** (`--interval 1 --max-frames 0`). A 533s clip yields ~533 per-second frames; nothing is skipped or capped. This is the baseline evidence.
- **Shot keyframes (frames/)**: scene-cut detection runs **automatically** and writes **large, original-resolution keyframe images into `frames/`** — one big image per detected shot change, for reading shot composition in detail. Tune sensitivity with `--cut-threshold` (0–100; higher = fewer cuts), and add `--scene-cuts` to also write `_cuts.txt` + beat statistics.
- **sheets/ holds both the compressed package and the paginated thumbnails**:
  - `压缩包_全部帧.jpg` — **one dense master image collapsing every per-second frame into a single file** (the "压缩每一帧的包" you keep).
  - `sheet_XX.jpg` — the same per-second frames laid out as readable **paginated thumbnails** (default 5×9 = 45/page).
- **Do not re-cap sampling**: never set `--max-frames` to a small number for long clips; that is what previously under-sampled. Leave it `0` (uncapped) unless you want a deliberate sparse probe. If the report's action beats disagree with a re-watch, the sampling was too sparse — re-run with the default uncapped setting.

## Retrieval fallback ladder
1. Run the script on the supplied URL/file before asking the user to upload anything.
2. If download fails, update `yt-dlp` and retry once only.
3. If available, inspect the page with a permitted browser/connector for video/captions.
4. Treat thumbnails and page metadata as metadata only, never as proof of the full video.
5. Captions/transcripts support dialogue and approximate timing only; they do not prove visuals.
6. If media remains inaccessible, report the exact limitation and ask for one simple fallback: an accessible direct media URL, local video file, or keyframes plus transcript. Never bypass DRM, private/login-only access, paywalls, or access controls.

## Workflow

### 1. Intake and evidence inventory
Record whether full video, sampled frames, scene-cut frames, audio, transcript, thumbnail/page metadata, or only technical metadata were available. Read `analysis_bundle.json`, `source_metadata.json`, and `access_diagnostic.json` if present. Inspect actual frame images; their existence is not proof they were visually inspected. Note the rhythm evidence: if scene-cut mode ran, read `extraction.avg_beats_per_second` and `extraction.scene_cuts` — this sizes how many beats each generation unit must hold.

### 2. Capture the rhythm and the action beats (most important, do before writing any prompt)
- Establish the **average beat interval**: `1 / avg_beats_per_second` (or cut count ÷ duration). Example: 231 cuts over 533s ≈ 2.3s/beat.
- Walk the frames **in order** and write down what is **actually visible** at each cut/interval as an ordered list of **action beats (动作模板)**: each beat is a concrete visible verb with a start → middle → end, e.g. `① subject A appears from sand ② A lunges mouth-first at B ③ B rears up and glares`.
- Do **not** invent beats the frames do not show. If a region is unclear, label it `unknown` and keep moving.
- Group beats into the natural generation units of the target model (e.g. Muse AI caps each clip at ~10s). A 10s unit at 2.3s/beat must hold **3–5 beats**, not "one slow action stretched to 10s". This is the #1 cause of flat, wrong regenerations.
- **Record every beat into `sheets/动作模板.md`** (the skeleton is auto-generated by `analyze_video.py`; you fill the per-sheet tables). This file is the single source of truth for the later shot breakdown — do not let the final prompt drift from it.

### 3. Analyze only what evidence supports
- **Hook and premise:** opening attention grabber, core idea, audience.
- **Narrative beats:** setup → development → escalation → payoff/ending, only where present.
- **Visual system:** subject, environment, props, wardrobe, composition, palette.
- **Shot language:** framing, **shot size**, **camera angle**, subject placement, **apparent camera movement**, focus cues.
- **Action and timing:** the ordered **action beats** from step 2; start/middle/end of each; pauses and reactions.
- **Lighting/color:** apparent direction, softness, contrast, exposure and palette; per-segment tone. Do not invent gear or numeric settings.
- **Sound:** dialogue, ambience, effects, music and sync only if audio/transcript supports it. For **dialogue-free** videos, still log non-verbal cues (grunts, gasps, ambient, stingers) — these become the sound column.
- **Editing/continuity:** shot changes, movement direction, eyelines, props/wardrobe, transitions; the **end frame** of each unit (the bridge to the next unit).
- **Transferable method:** explain likely creative purpose and generalize it without copying distinctive expression.
- **Improvement ideas:** label as suggestions, not observations.

### 4. Per-shot / per-unit schema (the core of the breakdown)
For every generation unit (or every distinguishable shot), record all of:

| 字段 | 说明 | 取值示例 |
|---|---|---|
| 时间区间 | 起止秒数 | `0–10s` / `120–130s` |
| 景别 | 画面范围 | 大远景 / 远景 / 全景 / 中景 / 中近景 / 近景 / 特写 / 大特写 |
| 机位 | 拍摄角度 | 平视 / 仰拍 / 俯拍 / 顶视 |
| 运动 | 摄像机运动 | 固定 / 推 / 拉 / 摇 / 移 / 跟 / 升降 / 环绕 / 手持 / 航拍 / 俯瞰 |
| 动作节拍 | 有序可见动作 ① ② ③，每拍有起承转合；禁止脑补 | `①A ②B ③C` |
| 声音 | 非语言音节 / 环境音 / 音乐提示（无声台词视频也要标） | `嗯/咝/风声/鼓点` |
| 段色调 | 本段统一色彩关键词，跨段只在边界换一次 | `暖橙沙漠` / `深蓝水下` |
| 结尾定格 | 本单元最后一帧画面，作为下一单元首帧（零跳变转场） | 描述末帧构图 |

Write the per-unit prompt as: **style sentence + shot size/angle + movement + `[剧情：…]` (the beats) + end-frame anchor**. Keep the style sentence verbatim (see §5). Characters appear only as placeholders (see §6).

### 5. Unified style sentence (anti-drift)
- Compose **one** fixed style sentence, e.g. `Pixar-style 3D animated film look, soft cinematic lighting, shallow depth of field, 16:9, consistent render style throughout` (or its Chinese equivalent).
- Paste it **verbatim** at the start of every unit prompt. Never paraphrase, translate loosely, or shorten it — most style drift comes from this sentence being edited per unit.
- Provide both a Chinese and an English version for the respective target models.

### 6. Character placeholder convention (makes the report reusable with any new character)
- Give each character a **placeholder token**: `[主角1]` / `[主角2]` / `[反派3]` … Do **not** hard-code names, species, or looks in the breakdown.
- In the textual prompt, describe **only action and expression** for a character; never its appearance. The appearance is locked by the reference image produced later by `image-reference-to-prompt`.
- Put a **role map** at the top of the report: `placeholder ↔ original-role-in-source ↔ reference-image-file`.
- Where a character is prone to deformation, add a short safeguard clause to that unit (e.g. `no wings, claws, or legs` / `blended into the unified animated render style`). Keep safeguards generic; specific examples belong in the character card from `image-reference-to-prompt`.

### 7. Fixed rules vs replaceable variables
**Fixed rules** (transferable, same every unit): the style sentence, the character card, the segment-color logic, the aspect ratio, the end-frame relay. Keep only rules supported by the reference or clearly labeled as improvements.

**Replaceable variables** are explicit fields, e.g. `[MAIN SUBJECT]`, `[SETTING]`, `[GOAL]`, `[OBSTACLE]`, `[KEY PROP]`, and the editable **`[剧情：…]`** block per unit (the colon is followed by the real observed beats; the user edits only the text after the colon, never the bracket structure). Do not mistake a reference's exact character, story, dialogue, or location for a fixed rule.

### 8. Generate and adapt prompt
Use `templates/master-prompt.md`. Fill known fields. For a ready-to-run prompt, do not leave placeholders unless the user asks for a template. Use observable, temporally coherent actions. Label each shot in multi-shot work and state continuity anchors. Keep creative prompt separate from model parameters. Only claim support for features/settings verified for the target model/version. Do not assume every model supports audio, negative prompts, reference images, fixed seeds, multi-shot generation, or identical duration/aspect controls.

### 9. Quality check
- Shot claims grounded in evidence; observation/inference/unknown separated.
- Each unit lists **ordered action beats** with a count consistent with the rhythm analysis (≈ duration ÷ beat interval).
- **Shot size, camera angle, and camera movement** are explicit for every unit and compatible with the action.
- Subject, wardrobe, props and location continuity are explicit; characters use placeholders, not descriptions.
- **Segment color tone** is stated and consistent within a unit.
- **End-frame anchor** is stated for every unit so units chain with zero jump.
- Payoff is readable and timed.
- Sound instructions supported by audio evidence (or explicitly logged as non-verbal cues for dialogue-free video).
- Style sentence is verbatim across units.
- Fixed rules separated from variables.
- Model parameters separated from prompt prose.
- Output is ready to use without requiring the user to learn the method.

## Output file naming
Never write a bare `video-prompt-report.md`. Append a short slug derived from the video so reports from different sources stay distinguishable:

`video-prompt-report-<slug>.md`

Slug rules:
- Source priority: video title → `uploader` + platform → local filename stem.
- Keep it short; an abbreviation is fine and preferred. Examples: `video-prompt-report-持械入宋.md`, `video-prompt-report-ESTEE-TVC.md`, `video-prompt-report-cat.md`.
- Use `-` as the separator. No spaces (they break URLs, shell quoting and some tools).
- Keep the title's original language — Chinese titles stay Chinese.
- Variants of the same source: append a qualifier after the slug, e.g. `video-prompt-report-商业宣传产品-拆分.md`.
- Unknown or unnameable source: use a neutral slug such as `clip1` rather than leaving the suffix off.
- Inside the report, state the source (platform + uploader/status id, or local filename) so the file is self-explanatory on its own.

## Default output structure
1. Access/evidence status (including sampling mode, cut count, avg beats/sec)
2. Creative summary: premise, hook, beats, payoff
3. **Role map** (placeholder ↔ source role ↔ reference image)
4. **Unified style sentence** (Chinese + English, verbatim)
5. **Rhythm constraint** (beat interval; how many beats per generation unit)
6. **Shot-by-shot / unit-by-unit breakdown** using the §4 schema (size, angle, movement, beats ①②③, sound, segment tone, end-frame anchor, CN + EN prompt)
7. Why it works (interpretation)
8. Fixed rules vs replaceable variables (incl. the `[剧情]` variable)
9. Ready-to-use prompt(s)
10. Supported model settings, if known
11. Two to four risks/next-iteration checks

## Generated output directory layout
`analyze_video.py` writes the following under `--out`:

- `frames/` — **shot keyframes as large original-resolution images** (one per detected scene cut). Big reference images for reading shot composition in detail; NOT the per-second thumbnails.
- `_everysec/` — **per-second thumbnail frames** (downscaled), the source for the sheets. Kept so `make_sheets.py` can rebuild pages without re-extracting.
- `sheets/` — the rhythm/action evidence package:
  - `压缩包_全部帧.jpg` — **the compressed package**: every per-second frame collapsed into one master image (the "压缩每一帧的包" you keep inside sheets/).
  - `sheet_XX.jpg` — paginated contact sheets (default 5×9 = 45 frames/page), built by the bundled `scripts/make_sheets.py`. Read these page by page to log beats.
  - `节奏实录.md` — per-second anchor skeleton (`[待填]` per second); **write-if-missing** so a re-run never overwrites your filled notes.
  - `动作模板.md` — **blank action-template skeleton** (from `templates/action-template.md`); **write-if-missing** (same protection). This is the source of truth for the breakdown.
  - `_cuts.txt` — scene-cut list + beat statistics (only with `--scene-cuts`).
  - `参考音轨_原片.wav` — the extracted reference audio (when present), for offline voiceover alignment.
- `roles/` — **empty by design**; the user drops adapted-character reference images here (e.g. `主角1.jpg`, `主角2.jpg`, `反派3.jpg`). A `README.txt` documents the naming convention. Never put analysis output in here.
- root: `analysis_bundle.json`, `source_metadata.json`, `audio.wav`, `transcript.txt`/`transcript.json` (if `--transcribe`). **No top-level `contact_sheet.jpg` is generated** — the compressed package lives in `sheets/`.

`make_sheets.py` is invoked automatically by `analyze_video.py`; it can also be run standalone (`python scripts/make_sheets.py --out <dir>`) to rebuild the paginated sheets after tweaking layout, without re-extracting frames.

When asked only to build or modify a Skill, provide the artifact rather than applying the workflow.

## Handoff to image-reference-to-prompt (the two skills are designed to chain)
- This skill outputs: **character placeholders + per-shot action/camera/size templates + a verbatim style sentence + end-frame anchors**. It deliberately contains **no character likeness**.
- Next, run `image-reference-to-prompt` on the user's new character reference image(s) to produce a **character card** (stable appearance in CN + EN, forbidden traits, consistency risks, expression/action range).
- Drop the character card into the matching `[主角N]` placeholder and load the reference image into the video model. Each shot prompt then carries the new character with correct action, camera, and size — without re-doing the shot breakdown.
- Changing the character never requires re-analyzing the video.

## Copyright and honesty
Do not imply the user owns the reference. Transfer high-level techniques while changing distinctive characters, dialogue and scene expression. Do not reproduce long copyrighted dialogue/lyrics. Never invent source access, timestamps, model settings, camera metadata, original prompts or seeds.
