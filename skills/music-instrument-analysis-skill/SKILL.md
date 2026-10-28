---
name: music-instrument-analysis
description: Given a piece of music (video URL or local uploaded file), identify the instrument lineup and explain each instrument's best use-cases and pairings, using objective YAMNet (ONNX) instrument probabilities + spectral features + musicology, with an optional timeline segmented arrangement table (which section uses what). Honestly labels inference confidence; never claims "100% automatic precision".
version: "2.1.0"
agent_created: true
triggers:
  - 识别乐器
  - 拆解配器
  - 这段音乐用了什么乐器
  - 分析乐器
  - 乐器讲解
  - 上传音乐识别乐器
  - 识别这段音乐的乐器
  - identify instruments
  - what instruments are used
---

# Music Instrument Analysis (v2)

## What it does
Input a piece of music (video URL / uploaded audio), output:
1. **Instrument lineup** (YAMNet objective probabilities + AI knowledge correction, layered by confidence)
2. Each instrument's **role** in the track
3. Each instrument's **best use-cases**
4. Each instrument's **best pairings** + reasoning
5. `has_voice` (whether vocals are present) — to judge "is it instrumental?"
6. **Timeline segmented arrangement table**: slice the audio into fixed windows
   (default 8s), give per-segment instruments, then merge into natural passages
   (Intro / VerseN / Bridge / Outro) — so you can **locate "which section likely
   uses what"** instead of merging the whole track into one list.

## Two-layer architecture
- **Layer 1 · Objective (YAMNet):** `scripts/analyze_instruments.py` calls YAMNet
  (ONNX, AudioSet 521 classes) to classify the waveform frame-by-frame. Whole-track
  mode takes the global `max` per class; segment mode takes the `max` within that
  time window, then filters to instrument/sound classes and groups into "families".
  This is **objective evidence**, not a guess.
- **Layer 2 · Knowledge (AI):** read YAMNet output + spectral features (band-energy
  ratios / centroid / onsets) + genre knowledge to make the final call and write
  the explanation.

Weights + class map live in `assets/` (`yamnet.onnx` 16MB + `yamnet_class_map.csv`).
**Missing? The script auto-downloads from the HF mirror (`HF_ENDPOINT=https://hf-mirror.com`).**

## Honest boundaries (enforce these — fight sycophancy)
- YAMNet is an **existence / family-level** classifier, not a note-by-note listener. Measured ability:
  - ✅ **Reliable:** percussion family (drums/cymbals/bells/steel drums…), **whether voice is present** (`has_voice` negative is very stable).
  - ⚠️ **Right direction, specific name unreliable:** plucked strings (harp/zheng vs sitar/mandolin/zither) — YAMNet can't tell them apart and mislabels; `Jingle bell` high score is often an over-trigger of "bright metallic percussion", not a literal Christmas bell.
  - ❌ **Misses:** piano sometimes doesn't enter top15 (YAMNet's Piano class may not fire) — then you **must** recover it via spectral mid-band body + decay envelope. So Layer 2 is mandatory.
- Academic SOTA (IRMAS multi-instrument test) micro/macro-F1 ≈ 0.69/0.63; real mixed tracks are lower. **There is no "automatically and precisely identify every instrument" — never write "precise identification" in the report.**
- Confidence layering:
  - **High:** YAMNet strong signal + spectral confirmation — percussion family, bass, obvious electric-guitar distortion, voice presence/absence.
  - **Mid:** YAMNet signal but easily confused — strings, woodwinds, harp/zheng, synth pad.
  - **Low:** YAMNet specific name suspicious or only genre-inferred — specific plucked type, synth imitating acoustic.
- Report MUST label confidence + **basis** (which feature / which YAMNet class supports it).
- **Segment-mode extra boundaries:**
  - Passage naming (Intro / VerseN / Bridge / Outro) is **heuristic**, not audio-structure analysis: first=Intro, last=Outro, onset-density drop=Bridge/Interlude, rest sequential "VerseN" (**only sequential numbering, not strict verse/chorus form**; especially for calm tracks). Allow the AI report to correct/rename.
  - **Fine timbre & playing technique YAMNet and spectrum both miss**: `808 bass` vs plain bass, `glide lead`, `arpeggio`, `specific synth model` — only directional guesses like "low-frequency heavy → bass/sub-bass", "melodic synth timbre", label confidence low, never write specific models.
  - Segment `--seg-len` default 8s; too short = noisy, too long = loses localization; longer tracks can use 10–12s.

## Workflow
1. **Get audio**
   - **URL** (Bilibili/YouTube/…): the script itself downloads the best audio track via `yt-dlp` (`--url`).
   - **Uploaded file**: use the local path directly (`--audio`).
2. **Non-ASCII path handling (Windows)**: Git-Bash passing Chinese args to native
   Windows programs (ffmpeg) mojibakes. The script has built-in `_ascii_safe()`:
   if the file name has non-ASCII it copies to an ASCII temp name. No manual step.
3. **Extract features (single command, auto-runs both layers)**
   ```bash
   python <skill>/scripts/analyze_instruments.py --audio <file.mp3|wav> \
        --out <stats.json> --png <spectrogram.png> [--seg-len 8]
   # or from a URL:
   python <skill>/scripts/analyze_instruments.py --url <video URL> \
        --out <stats.json> --png <spectrogram.png> [--seg-len 8]
   ```
   - `--seg-len N`: timeline segment length (s), default 8; `0` disables segmentation (whole-track only).
   - Output `stats.json`:
     - `low_ratio/mid_ratio/high_ratio`, `spectral_centroid_hz`, `onset_rate_per_s`, `rms`, `duration_s` (whole-track spectral layer)
     - `yamnet`: whole-track `{ available, instruments:[{name,class,score,family}], families:[{family,score}], has_voice }`
     - `segments` (only when `--seg-len>0`): each N-second segment; each segment's `instruments` includes YAMNet hits and `source:"spectrum"` fallbacks, `families`, `onset_rate_per_s`, `has_voice`
     - `structure`: merged natural passages with `label` (Intro/VerseN/Bridge/Outro, "inferred"), `start/end`, `top_instruments`, `onset_rate_per_s`, `reason`
     - Skip YAMNet (and segmentation): `--no-yamnet`.
4. **AI infers instruments**
   - First read `yamnet.instruments`/`families` for objective probabilities, **trust strong signals and `has_voice` first**.
   - Read spectrum: sustained low freq = bass/drums; mid-band body = piano/strings (recover when piano is missed); high-freq sparkle = flute/bell/cymbal; onset density = rhythmic percussion/plucking.
   - Combine genre (new-age / Japanese healing / classical / J-Pop…) to correct YAMNet's easily-wrong specific names (e.g. "sitar" → "harp/zheng" direction).
   - Output a list, each item with **confidence + basis**.
5. **Explain** (for ≥ mid-confidence instruments): use-case + best pairing + one-line reason.
6. **Report**: markdown, with instrument table (name/confidence/basis) + per-item explanation + spectrogram.

## Dependencies
- `ffmpeg` + Python packages `numpy` `scipy` `matplotlib` `onnxruntime` + weights `yamnet.onnx`/`yamnet_class_map.csv` (auto-downloaded).
- Verified env: a venv with the above packages + weights. On a fresh machine:
  `python -m pip install numpy scipy matplotlib onnxruntime`; weights auto-pull on first run.

## Output example (structure)
```
0:00–0:08  前奏：底鼓/打击(YAMNet)、贝斯(频谱推断)、合成 pad 铺底；鼓密度低，留白多
0:08–0:56  主歌1–4：贝斯+钢琴/弦乐铺底持续；32–40s 出现 YAMNet「铃/钟」高频点缀(可能过触发)
1:12–1:20  桥段：鼓撤掉(onset 骤降)，只剩贝斯+钢琴铺底+弹拨(竖琴/筝类)点缀，留白
1:20–3:04  主歌5–7：配器回满，贝斯+鼓+钢琴+高频色彩
3:36–3:56  尾奏：鼓撤掉，钢琴/弦乐渐弱收束
has_voice: false（纯音乐）
```
Note: the above is illustrative; the actual report is generated by the AI reading
the `structure` field, labeling each instrument's source (YAMNet objective /
spectral inference / genre correction) and confidence.
