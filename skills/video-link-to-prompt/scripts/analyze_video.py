#!/usr/bin/env python3
"""Extract technical evidence from a URL or local video; does not semantically understand frames."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

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

def extract_frames(media, out_dir, interval, max_frames, duration):
    if not shutil.which("ffmpeg"): raise RuntimeError("ffmpeg is not installed or not on PATH")
    folder = out_dir / "frames"; folder.mkdir(parents=True, exist_ok=True)
    times = []
    if duration and duration > 0:
        t = 0.0
        while t < duration and len(times) < max_frames:
            times.append(t); t += interval
    else: times = [i * interval for i in range(max_frames)]
    records = []
    for t in times:
        idx = len(records) + 1
        name = f"frame_{idx:04d}_{t:010.3f}.jpg"; target = folder / name
        p = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(media), "-frames:v", "1", "-q:v", "3", str(target)], 45)
        if p.returncode == 0 and target.exists() and target.stat().st_size:
            records.append({"index": idx, "timestamp_seconds": round(t, 3), "filename": f"frames/{name}", "label": f"{t:.2f}s"})
        elif target.exists(): target.unlink()
    return records

def make_contact_sheet(out_dir, frames, cols=4):
    try: from PIL import Image, ImageDraw
    except ImportError: return None
    items = []
    for frame in frames:
        try:
            im = Image.open(out_dir / frame["filename"]).convert("RGB"); im.thumbnail((360, 220))
            items.append((im.copy(), frame["label"]))
        except Exception: pass
    if not items: return None
    cw, ch, lh = 380, 250, 28; rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*cw, rows*(ch+lh)), "white"); draw = ImageDraw.Draw(sheet)
    for i, (im, label) in enumerate(items):
        x=(i%cols)*cw; y=(i//cols)*(ch+lh)
        sheet.paste(im, (x+(cw-im.width)//2, y+(ch-im.height)//2)); draw.text((x+8, y+ch+4), label, fill="black")
    sheet.save(out_dir / "contact_sheet.jpg", quality=88)
    return "contact_sheet.jpg"

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
    ap.add_argument("--out", required=True); ap.add_argument("--interval", type=float, default=1.0); ap.add_argument("--max-frames", type=int, default=60)
    ap.add_argument("--transcribe", action="store_true"); ap.add_argument("--whisper-model", default="small")
    args = ap.parse_args()
    if args.interval <= 0 or args.max_frames < 1: ap.error("--interval must be > 0 and --max-frames >= 1")
    out = Path(args.out).expanduser().resolve(); out.mkdir(parents=True, exist_ok=True); started = time.time()
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
    try: frames = extract_frames(media, out, args.interval, args.max_frames, media_info.get("duration_seconds")); frame_error = None
    except Exception as e: frames=[]; frame_error=f"{type(e).__name__}: {e}"
    contact = make_contact_sheet(out, frames)
    audio, audio_error = extract_audio(media, out) if media_info.get("audio_present") else (None, "No audio stream reported")
    transcript = transcribe(out/audio, out, args.whisper_model) if args.transcribe and audio else None
    notes = ["Technical extraction only; this script does not semantically interpret visual content.", "Evenly sampled frames may miss fast cuts and brief actions.", "Use the host agent's actual image-understanding capability; do not assume it happened automatically."]
    if frame_error: notes.append("Frame extraction issue: " + frame_error)
    if audio_error: notes.append("Audio extraction note: " + audio_error)
    file_map = {"media_file":str(media),"contact_sheet":contact,"audio":audio}
    if transcript and transcript.get("ok"): file_map.update({"transcript_text":"transcript.txt","transcript_json":"transcript.json"})
    bundle = {"schema_version":SCHEMA,"status":"ok" if frames else "partial","source":source,"media":media_info,"extraction":{"sampling_interval_seconds":args.interval,"max_frames":args.max_frames,"frame_count":len(frames),"audio_extracted":bool(audio),"transcription_requested":args.transcribe,"transcription":transcript},"frames":frames,"files":file_map,"notes":notes,"elapsed_seconds":round(time.time()-started,2)}
    write_json(out / "analysis_bundle.json", bundle)
    print(json.dumps({"status":bundle["status"],"out_dir":str(out),"frame_count":len(frames),"contact_sheet":contact,"audio_extracted":bool(audio),"bundle":str(out/"analysis_bundle.json"),"notes":notes}, ensure_ascii=False, indent=2))
    return 0 if frames else 4

if __name__ == "__main__": raise SystemExit(main())
