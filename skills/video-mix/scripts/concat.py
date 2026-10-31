#!/usr/bin/env python3
"""
video-mix: concatenate all mp4 clips in a directory (in filename order) into
one video, optionally mix in a generated background music track.

Agent-agnostic. Any AI agent can call:
    python concat.py --input-dir "/path/to/clips"
        -> concatenate silently, print JSON with total_duration
    python concat.py --input-dir "/path/to/clips" --music /path/to/bgm.wav
        -> concatenate + mux music, print JSON with output_path

Requirements: ffmpeg + ffprobe on PATH.
Output is always H.264 + AAC with `-movflags +faststart` so it uploads cleanly
to X/Twitter, Douyin, WeChat, etc.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys


def run(cmd, env=None):
    return subprocess.run(cmd, text=True, capture_output=True, env=env)


def ffprobe_video(path):
    """Return dict: duration, width, height, fps."""
    out = run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-show_entries", "stream=codec_type,width,height,r_frame_rate",
        "-of", "json", path,
    ])
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {out.stderr}")
    data = json.loads(out.stdout)
    vs = next(s for s in data["streams"] if s["codec_type"] == "video")
    return {
        "path": path,
        "name": os.path.basename(path),
        "duration": float(data["format"]["duration"]),
        "width": int(vs["width"]),
        "height": int(vs["height"]),
        "fps": vs["r_frame_rate"],
    }


def main():
    ap = argparse.ArgumentParser(description="Concatenate mp4 clips and optionally mix in background music.")
    ap.add_argument("--input-dir", required=True, help="Directory containing source mp4 clips.")
    ap.add_argument("--music", default="", help="Path to background music wav/mp3 (optional).")
    ap.add_argument("--output-name", default="", help="Output filename (default: <dir_name>_mixed.mp4).")
    args = ap.parse_args()

    in_dir = args.input_dir
    if not os.path.isdir(in_dir):
        print(json.dumps({"success": False, "error": f"目录不存在: {in_dir}"}, ensure_ascii=False))
        sys.exit(1)

    work = os.path.join(in_dir, "_work")
    os.makedirs(work, exist_ok=True)

    # 1. Scan mp4 files (exclude _work and prior mixed outputs)
    skip_pattern = re.compile(r"_(?:mixed|合成版|配乐版|merged)\.mp4$", re.IGNORECASE)
    clips = []
    for f in sorted(os.listdir(in_dir)):
        if not f.lower().endswith(".mp4"):
            continue
        full = os.path.join(in_dir, f)
        if not os.path.isfile(full):
            continue
        if os.path.dirname(full) == work:
            continue
        if skip_pattern.search(f):
            continue
        clips.append(full)

    if not clips:
        print(json.dumps({"success": False, "error": f"目录下没有 mp4 文件: {in_dir}"}, ensure_ascii=False))
        sys.exit(1)

    # 2. Probe each clip, check resolution/fps consistency
    probes = [ffprobe_video(p) for p in clips]
    ref = probes[0]
    mismatched = [p for p in probes if p["width"] != ref["width"] or p["height"] != ref["height"] or p["fps"] != ref["fps"]]
    if mismatched:
        print(json.dumps({
            "success": False,
            "error": "视频分辨率或帧率不一致，无法无损拼接: " + ", ".join(p["name"] for p in mismatched),
            "expected": {"width": ref["width"], "height": ref["height"], "fps": ref["fps"]},
        }, ensure_ascii=False))
        sys.exit(1)

    total = sum(p["duration"] for p in probes)

    # 3. Write concat list (no BOM, forward slashes)
    list_path = os.path.join(work, "concat.txt")
    with open(list_path, "w", encoding="utf-8", newline="\n") as fh:
        for p in probes:
            safe = p["path"].replace("\\", "/").replace("'", "'\\''")
            fh.write(f"file '{safe}'\n")

    # 4. Concatenate silently
    merged = os.path.join(work, "merged_silent.mp4")
    r = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-an", "-c:v", "copy", merged])
    if r.returncode != 0 or not os.path.isfile(merged):
        print(json.dumps({"success": False, "error": "ffmpeg concat 失败", "stderr": r.stderr[-500:]}, ensure_ascii=False))
        sys.exit(1)

    # 5. If no music, return concat-only result
    if not args.music:
        print(json.dumps({
            "success": True,
            "mode": "concat_only",
            "input_dir": in_dir,
            "files": [p["name"] for p in probes],
            "total_duration": round(total, 2),
            "width": ref["width"],
            "height": ref["height"],
            "fps": ref["fps"],
            "merged_silent": merged,
            "work_dir": work,
        }, ensure_ascii=False))
        sys.exit(0)

    # 6. Mux music
    if not os.path.isfile(args.music):
        print(json.dumps({"success": False, "error": f"音乐文件不存在: {args.music}"}, ensure_ascii=False))
        sys.exit(1)

    out_name = args.output_name or f"{os.path.basename(in_dir)}_mixed.mp4"
    out_path = os.path.join(in_dir, out_name)

    r = run([
        "ffmpeg", "-y",
        "-i", merged, "-i", args.music,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        out_path,
    ])
    if r.returncode != 0 or not os.path.isfile(out_path):
        print(json.dumps({"success": False, "error": "ffmpeg 混合失败", "stderr": r.stderr[-500:]}, ensure_ascii=False))
        sys.exit(1)

    # Final probe
    fp = run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "json", out_path,
    ])
    try:
        fdata = json.loads(fp.stdout)["format"]
    except Exception:
        fdata = {"duration": total, "size": os.path.getsize(out_path)}

    print(json.dumps({
        "success": True,
        "mode": "muxed",
        "input_dir": in_dir,
        "files": [p["name"] for p in probes],
        "total_duration": round(total, 2),
        "output_path": out_path,
        "output_duration": round(float(fdata["duration"]), 2),
        "output_size_bytes": int(fdata["size"]),
        "width": ref["width"],
        "height": ref["height"],
        "fps": ref["fps"],
        "work_dir": work,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
