#!/usr/bin/env python3
"""Extract technical evidence from a URL or local video; does not semantically understand frames."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from make_sheets import make_sheets

SCHEMA = "video-evidence-v1"

def run(cmd, timeout=120):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def version(exe, args):
    if not shutil.which(exe): return None
    try:
        p = run([exe, *args], 20)
        return ((p.stdout or p.stderr).strip().splitlines() or ["available"])[0][:300]
    except Exception: return "available; version check failed"

def download_url(url, out_dir):
    if not shutil.which("yt-dlp"):
        return None, {"ok": False, "error": "yt-dlp is not installed or not on PATH", "next_step": "Run: python -m pip install -r requirements.txt"}
    folder = out_dir / "source"
    folder.mkdir(parents=True, exist_ok=True)
    template = str(folder / "source.%(ext)s")
    cmd = ["yt-dlp", "--no-playlist", "--no-warnings", "-f", "bv*+ba/b", "--merge-output-format", "mp4", "-o", template, "--print", "after_move:filepath", url]
    try:
        p = run(cmd, 900)
        for line in reversed((p.stdout or "").splitlines()):
            candidate = Path(line.strip())
            if candidate.is_file() and candidate.stat().st_size:
                return candidate, {"ok": True, "tool": "yt-dlp", "stderr_tail": (p.stderr or "")[-1200:]}
        found = [x for x in folder.iterdir() if x.is_file() and x.stat().st_size]
        if p.returncode == 0 and found:
            return max(found, key=lambda x: x.stat().st_mtime), {"ok": True, "tool": "yt-dlp", "note": "Located output by scanning download folder"}
        return None, {"ok": False, "returncode": p.returncode, "error": (p.stderr or p.stdout or "No media file produced")[-2500:], "next_step": "Update yt-dlp and retry once; if access remains blocked, use a permitted direct media URL or local file."}
    except subprocess.TimeoutExpired:
        return None, {"ok": False, "error": "Download timed out after 15 minutes", "next_step": "Try a direct media URL or local file."}
    except Exception as e:
        return None, {"ok": False, "error": f"{type(e).__name__}: {e}"}

def probe(path):
    if not shutil.which("ffprobe"): return {"ok": False, "error": "ffprobe is not installed or not on PATH"}
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration,format_name,size:stream=codec_type,codec_name,width,height,avg_frame_rate", "-of", "json", str(path)], 60)
    if p.returncode: return {"ok": False, "error": (p.stderr or "ffprobe failed")[-2000:]}
    try: raw = json.loads(p.stdout)
    except json.JSONDecodeError: return {"ok": False, "error": "Could not parse ffprobe output"}
    fmt = raw.get("format", {}); streams = raw.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    try: duration = float(fmt.get("duration")) if fmt.get("duration") else None
    except (ValueError, TypeError): duration = None
    fps = None
    try:
        num, den = v.get("avg_frame_rate", "0/0").split("/")
        fps = float(num) / float(den) if float(den) else None
    except Exception: pass
    return {"ok": True, "duration_seconds": duration, "format_name": fmt.get("format_name"), "size_bytes": fmt.get("size"), "width": v.get("width"), "height": v.get("height"), "fps": fps, "video_codec": v.get("codec_name"), "audio_present": bool(a), "audio_codec": a.get("codec_name") if a else None}

def detect_scene_cuts(media, threshold, max_frames):
    """Return list of scene-cut timestamps via ffmpeg scdet filter. None on failure.
    threshold is on scdet's 0-100 scale (percent of frame change)."""
    if not shutil.which("ffmpeg"): return None, "ffmpeg not installed"
    try:
        p = run(["ffmpeg", "-hide_banner", "-i", str(media),
                 "-filter:v", f"scdet=threshold={threshold}",
                 "-f", "null", "-"], 300)
        cuts = []
        for line in (p.stderr or "").splitlines():
            m = re.search(r"lavfi\.scd\.time:\s*(\d+\.?\d*)", line)
            if m:
                cuts.append(round(float(m.group(1)), 3))
        seen = set(); uniq = []
        for c in cuts:
            if c not in seen:
                seen.add(c); uniq.append(c)
        if max_frames and len(uniq) > max_frames:
            uniq = uniq[:max_frames]
        return uniq, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def extract_frames(media, out_dir, interval, max_frames, duration, times=None, subdir="frames", resize=None, clear_old=True):
    """Extract frames into out_dir/<subdir>.

    - times=None  -> even sampling at `interval` seconds (dense, full-coverage). When
      max_frames<=0 there is no cap, so a clip is sampled one frame per `interval`
      (default 1s) across its whole duration (逐秒逐帧解析).
    - times=list  -> extract exactly those timestamps (e.g. scene-cut keyframes).
    - resize=W    -> downscale to width W (used for per-second thumbnails that feed
      the sheets). Keyframes pass None to keep original resolution (large images).
    - clear_old   -> remove stale frame_*.jpg in the subdir before extracting, so a
      re-run never mixes old and new frames in the same folder.
    """
    if not shutil.which("ffmpeg"): raise RuntimeError("ffmpeg is not installed or not on PATH")
    folder = out_dir / subdir; folder.mkdir(parents=True, exist_ok=True)
    if clear_old:
        for old in folder.glob("frame_*.jpg"):
            try: old.unlink()
            except OSError: pass
    if times is None:
        times = []
        if duration and duration > 0:
            t = 0.0
            while (max_frames <= 0 or len(times) < max_frames) and t < duration:
                times.append(t); t += interval
            if duration and (max_frames <= 0 or len(times) < max_frames):
                times.append(round(duration, 3))
        else:
            times = [i * interval for i in range(max_frames if max_frames > 0 else 0)]
    records = []
    vf = ["scale=%d:-2" % resize] if resize else None
    for t in times:
        idx = len(records) + 1
        name = f"frame_{idx:04d}_{t:010.3f}.jpg"; target = folder / name
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(media), "-frames:v", "1"]
        if vf: cmd += ["-vf", vf[0]]
        cmd += ["-q:v", "3", str(target)]
        p = run(cmd, 45)
        if p.returncode == 0 and target.exists() and target.stat().st_size:
            records.append({"index": idx, "timestamp_seconds": round(t, 3), "filename": f"{subdir}/{name}", "label": f"{t:.2f}s"})
        elif target.exists():
            try: target.unlink()
            except OSError: pass
    return records

def make_compressed_archive(out_dir, sheets_dir, frames, thumb=(220, 124), cols=11, quality=86):
    """Build ONE dense master image containing every per-second frame, written to
    sheets/压缩包_全部帧.jpg. This is the 'compressed all-frames package' (压缩每一帧的包)
    that lives inside sheets/. Each second collapses into one cell of a single file."""
    try: from PIL import Image, ImageDraw
    except ImportError: return None
    items = []
    for frame in frames:
        try:
            im = Image.open(out_dir / frame["filename"]).convert("RGB"); im.thumbnail(thumb)
            items.append((im.copy(), frame["label"]))
        except Exception: pass
    if not items: return None
    items.sort(key=lambda t: float((t[1].rstrip("s") or 0) or 0))
    cw, ch, lh = thumb[0] + 6, thumb[1] + 20, 0
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*cw, rows*(ch+lh)), "white"); draw = ImageDraw.Draw(sheet)
    for i, (im, label) in enumerate(items):
        x = (i % cols) * cw; y = (i // cols) * (ch + lh)
        sheet.paste(im, (x + (cw - im.width)//2, y + (ch - im.height)//2))
        draw.rectangle([x, y, x + cw - 2, y + ch - 2], outline=(210, 210, 210))
        draw.text((x + 2, y + ch - 16), f"{label}", fill="black")
    name = "压缩包_全部帧.jpg"
    sheets_dir.mkdir(parents=True, exist_ok=True)
    sheet.save(sheets_dir / name, quality=quality)
    return f"sheets/{name}"

def extract_audio(media, out_dir):
    if not shutil.which("ffmpeg"): return None, "ffmpeg not installed"
    target = out_dir / "audio.wav"
    p = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(target)], 300)
    if p.returncode == 0 and target.exists() and target.stat().st_size > 44: return "audio.wav", None
    if target.exists(): target.unlink()
    return None, (p.stderr or "No audio stream or extraction failed")[-1000:]

def transcribe(audio, out_dir, model_name):
    try: from faster_whisper import WhisperModel
    except ImportError: return {"ok": False, "error": "faster-whisper not installed", "next_step": "Optional: python -m pip install faster-whisper"}
    try:
        model = WhisperModel(model_name, device="auto", compute_type="int8")
        segments, info = model.transcribe(str(audio), vad_filter=True)
        rows = [{"start": round(float(s.start), 3), "end": round(float(s.end), 3), "text": s.text.strip()} for s in segments]
        (out_dir / "transcript.txt").write_text("\n".join(f"[{r['start']:.2f}-{r['end']:.2f}] {r['text']}" for r in rows), encoding="utf-8")
        write_json(out_dir / "transcript.json", {"language": getattr(info, "language", None), "segments": rows})
        return {"ok": True, "language": getattr(info, "language", None), "segment_count": len(rows)}
    except Exception as e: return {"ok": False, "error": f"{type(e).__name__}: {e}"}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True); group.add_argument("--url"); group.add_argument("--file")
    ap.add_argument("--out", required=True); ap.add_argument("--interval", type=float, default=1.0); ap.add_argument("--max-frames", type=int, default=0)
    ap.add_argument("--transcribe", action="store_true"); ap.add_argument("--whisper-model", default="small")
    ap.add_argument("--scene-cuts", action="store_true", help="（已弃用）场景切点仅作节奏参考，不影响拆帧；frames/ 始终为逐秒大图。")
    ap.add_argument("--cut-threshold", type=float, default=10.0, help="scdet sensitivity for --scene-cuts on a 0-100 scale; higher = fewer cuts.")
    args = ap.parse_args()
    if args.interval <= 0 or args.max_frames < 0: ap.error("--interval must be > 0 and --max-frames >= 0 (0 = uncapped)")
    out = Path(args.out).expanduser().resolve(); out.mkdir(parents=True, exist_ok=True); started = time.time()
    sheets_dir = out / "sheets"; sheets_dir.mkdir(parents=True, exist_ok=True)
    roles_dir = out / "roles"; roles_dir.mkdir(parents=True, exist_ok=True)
    (roles_dir / "README.txt").write_text(
        "把改编角色的参考图放在这里，供 image-reference-to-prompt 生成角色卡。\n"
        "建议命名：主角1.jpg / 主角2.jpg / 反派3.jpg … 与分镜报告里的占位符一一对应。\n"
        "本目录由 video-link-to-prompt 自动创建，保持为空，仅用于存放你的角色图。\n", encoding="utf-8")
    source = {"type": "url" if args.url else "file", "url": args.url, "input_file": args.file}
    if args.url: media, retrieval = download_url(args.url, out)
    else:
        candidate = Path(args.file).expanduser().resolve(); media = candidate if candidate.is_file() else None
        retrieval = {"ok": bool(media), "source": "local file" if media else None, "error": None if media else f"Local file does not exist: {candidate}"}
    metadata = {"schema_version": SCHEMA, "source": source, "retrieval": retrieval, "tools": {"yt_dlp": version("yt-dlp", ["--version"]), "ffmpeg": version("ffmpeg", ["-version"]), "ffprobe": version("ffprobe", ["-version"])}, "created_unix": int(time.time())}
    write_json(out / "source_metadata.json", metadata)
    if not media:
        diagnostic = {"status": "failed", "stage": "retrieval", "error": retrieval.get("error", "Media could not be retrieved"), "details": retrieval, "next_steps": ["Update yt-dlp and retry once if URL is public.", "Do not bypass access controls.", "Provide an accessible direct media URL or local file.", "Alternatively provide keyframes and transcript/audio notes."]}
        write_json(out / "access_diagnostic.json", diagnostic)
        write_json(out / "analysis_bundle.json", {"schema_version": SCHEMA, "status": "failed", "source": source, "media": None, "extraction": {"frame_count": 0}, "frames": [], "files": {}, "notes": [diagnostic["error"]]})
        print(json.dumps({"status":"failed","out_dir":str(out),"diagnostic":str(out/"access_diagnostic.json")}, ensure_ascii=False, indent=2)); return 2
    media_info = probe(media)
    if not media_info.get("ok"):
        diagnostic = {"status":"failed","stage":"probe","media_file":str(media),"error":media_info.get("error"),"next_steps":["Check FFmpeg/FFprobe installation.","Try a valid local media file."]}
        write_json(out / "access_diagnostic.json", diagnostic); write_json(out / "analysis_bundle.json", {"schema_version":SCHEMA,"status":"failed","source":source,"media":media_info,"extraction":{},"frames":[],"files":{},"notes":[diagnostic["error"]]})
        print(json.dumps(diagnostic, ensure_ascii=False, indent=2)); return 3
    notes = ["Technical extraction only; this script does not semantically interpret visual content.", "Use the host agent's actual image-understanding capability; do not assume it happened automatically."]
    duration = media_info.get("duration_seconds")
    # 通道1：逐秒大图（默认每秒1帧、不封顶），原分辨率大图直接存 frames/ —— 主拆帧输出
    everysec = extract_frames(media, out, args.interval, args.max_frames, duration, subdir="frames", resize=None)
    frame_error = None if everysec else "No per-second frames extracted"
    # 场景切点检测（仅作节奏参考 & 标记切点，不再单独抽大图；逐秒大图已含于 frames/）
    scene_cuts, sc_err = detect_scene_cuts(media, args.cut_threshold, 0)
    key_frames = []  # 不再单独抽大图关键帧，避免与逐秒大图重复
    if scene_cuts:
        print(json.dumps({"scene_cuts_detected": len(scene_cuts), "first_few": scene_cuts[:20], "threshold": args.cut_threshold}, ensure_ascii=False))
    elif sc_err:
        notes.append("Scene-cut detection failed: " + sc_err)
    frames = everysec  # bundle.frames = 逐秒帧全量证据（向后兼容 make_sheets 读取）
    # sheets 压缩包：所有逐秒帧压成一张总图（压缩每一帧的包）
    contact = make_compressed_archive(out, sheets_dir, everysec)
    audio, audio_error = extract_audio(media, out) if media_info.get("audio_present") else (None, "No audio stream reported")
    transcript = transcribe(out/audio, out, args.whisper_model) if args.transcribe and audio else None
    avg_bps = (len(scene_cuts)/duration) if (scene_cuts and duration) else None
    beat_interval = round(1/avg_bps, 2) if avg_bps else None
    if scene_cuts:
        notes.append(f"Detected {len(scene_cuts)} scene cuts (~{beat_interval}s/beat, {round(avg_bps,2)} beats/sec); 节奏实录.md 以 ✔ 标记切点秒。每个生成单元应容纳数个 beat，而非把慢动作拉成整段。")
    if not scene_cuts:
        notes.append("未检测到硬切（静态/渐变转场多的片段）；frames/ 仍为逐秒大图，节奏以逐秒为准。")
    if frame_error: notes.append("Frame extraction issue: " + frame_error)
    if audio_error: notes.append("Audio extraction note: " + audio_error)

    # ---- sheets 证据包：分页小图 + 节奏实录 + 动作模板（均 write-if-missing，重跑不覆盖已填） ----
    pages = make_sheets(out, sheets_dir, everysec)
    if not pages:
        notes.append("分页缩略图未能生成（Pillow 缺失或无逐秒帧）。请安装 Pillow 或直接读 _everysec/ 单帧后填写。")
    # 切点统计文件（仅 --scene-cuts 时写，作为节奏参考）
    cuts_file = None
    if scene_cuts:
        cuts_file = "sheets/_cuts.txt"
        lines = [f"scene cuts: {len(scene_cuts)}", f"threshold(scdet 0-100): {args.cut_threshold}",
                 f"avg beats/sec: {round(avg_bps, 3) if avg_bps else 'n/a'}", f"avg seconds/beat: {beat_interval if beat_interval else 'n/a'}", ""]
        lines += [f"{i+1:04d}\t{t}s" for i, t in enumerate(scene_cuts)]
        (sheets_dir / "_cuts.txt").write_text("\n".join(lines), encoding="utf-8")
    # 参考音轨复制
    ref_audio = None
    if audio:
        try:
            shutil.copy2(out / audio, sheets_dir / "参考音轨_原片.wav"); ref_audio = "sheets/参考音轨_原片.wav"
        except Exception: pass
    # 节奏实录.md（已存在则跳过，保护已填内容）
    rhythm_path = sheets_dir / "节奏实录.md"
    if not rhythm_path.exists():
        rlines = ["# 节奏实录（逐秒锚点，供填写实际画面）\n",
                  f"> 视频时长约 {round(duration,1) if duration else '?'}s，逐秒拆解；`[待填]` 处写该秒实际可见内容。\n",
                  "| 秒 | 时间轴 | 画面 / 动作（待填） | 关键帧大图 |",
                  "|---|---|---|---|"]
        for fr in everysec:
            ts = fr["timestamp_seconds"]
            has_key = "✔" if scene_cuts and any(abs(c - ts) < 0.5 for c in scene_cuts) else ""
            rlines.append(f"| {ts:.0f} | {ts:.2f}s | `[待填]` | {has_key} |")
        rhythm_path.write_text("\n".join(rlines) + "\n", encoding="utf-8")
    # 动作模板.md（已存在则跳过）
    action_template = "sheets/动作模板.md"
    if not (sheets_dir / "动作模板.md").exists():
        tpl_path = _SCRIPT_DIR.parent / "templates" / "action-template.md"
        try:
            header = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else "# 动作模板（原视频逐镜头动作拆解）\n\n"
        except Exception:
            header = "# 动作模板（原视频逐镜头动作拆解）\n\n"
        header = header.replace("{{beat_interval}}", str(beat_interval if beat_interval else "未知"))
        header = header.replace("{{beats_per_unit}}", f"（生成单元秒数 ÷ {beat_interval}s）" if beat_interval else "未知")
        header = re.sub(r"<!--SHEET_SECTIONS-->\s*", "", header)
        section_lines = [header.rstrip()]
        if pages:
            for idx, pg in enumerate(pages, 1):
                dur = max(pg["t_end"] - pg["t_start"], 0.0)
                n_rows = 3
                if beat_interval:
                    n_rows = max(3, min(20, int(round(dur / beat_interval)) + 1))
                section_lines.append(f"\n## sheet_{idx:02d}（{pg['t_start']}–{pg['t_end']}s，共 {pg['count']} 帧）\n")
                section_lines.append("| 时间区间 | 景别 | 机位 | 运动 | 动作节拍（①②③，每拍起承转合） | 声音 |")
                section_lines.append("|---|---|---|---|---|---|")
                for r in range(n_rows):
                    a = pg["t_start"] + dur * r / n_rows; b = pg["t_start"] + dur * (r + 1) / n_rows
                    section_lines.append(f"| {a:.2f}–{b:.2f}s |  |  |  |  |  |")
                section_lines.append(f"\n> 逐页阅读 sheets/sheet_{idx:02d}.jpg，按上表填写；看不清标 `unknown`。")
        else:
            section_lines.append("\n> 未生成分页缩略图（Pillow 缺失或无可读帧）。请直接阅读 _everysec/ 单帧后填写。")
        (sheets_dir / "动作模板.md").write_text("\n".join(section_lines) + "\n", encoding="utf-8")

    file_map = {"media_file":str(media),"compressed_archive":contact,"per_second_frames_dir":"frames",
                "keyframe_dir":"frames","audio":audio,"sheets_dir":"sheets","roles_dir":"roles",
                "action_template":action_template,"rhythm_record":"sheets/节奏实录.md",
                "cuts_list":cuts_file,"reference_audio":ref_audio,
                "sheet_pages":[p["file"] for p in pages],"keyframe_count":len(key_frames),"per_second_count":len(everysec)}
    if transcript and transcript.get("ok"): file_map.update({"transcript_text":"transcript.txt","transcript_json":"transcript.json"})
    bundle = {"schema_version":SCHEMA,"status":"ok" if everysec else "partial","source":source,"media":media_info,
              "extraction":{"sampling_interval_seconds":args.interval,"max_frames":args.max_frames,"per_second_count":len(everysec),
                            "keyframe_count":len(key_frames),"scene_cut_mode":bool(args.scene_cuts),
                            "scene_cuts":len(scene_cuts) if scene_cuts else None,"cut_threshold":args.cut_threshold,
                            "avg_beats_per_second":avg_bps,"audio_extracted":bool(audio),"transcription_requested":args.transcribe,"transcription":transcript},
              "frames":everysec,"files":file_map,"notes":notes,"elapsed_seconds":round(time.time()-started,2)}
    write_json(out / "analysis_bundle.json", bundle)
    print(json.dumps({"status":bundle["status"],"out_dir":str(out),"per_second_count":len(everysec),"keyframe_count":len(key_frames),
                      "scene_cuts":len(scene_cuts) if scene_cuts else None,"avg_beats_per_second":avg_bps,
                      "compressed_archive":contact,"sheets_pages":len(pages),"rhythm_record":"sheets/节奏实录.md",
                      "action_template":action_template,"audio_extracted":bool(audio),"bundle":str(out/"analysis_bundle.json"),"notes":notes}, ensure_ascii=False, indent=2))
    return 0 if everysec else 4

if __name__ == "__main__": raise SystemExit(main())
