#!/usr/bin/env python3
"""Extract technical evidence from a URL or local video; does not semantically understand frames."""
from __future__ import annotations
import argparse, json, math, re, shutil, subprocess, sys, time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from make_sheets import make_sheets
from frame_quality import analyze_series

SCHEMA = "video-evidence-v1"

def run(cmd, timeout=120):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def safe_remove(path):
    """Delete a file, but fall back to rename-into-trash when the sandbox blocks
    unlink (default safe-delete policy). Renaming never requires delete rights."""
    try:
        path.unlink()
    except OSError:
        try:
            trash = path.parent.parent / "_trash" / path.parent.name
            trash.mkdir(parents=True, exist_ok=True)
            path.rename(trash / f"{path.stem}.{int(time.time()*1000)}{path.suffix}")
        except Exception:
            pass

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

def extract_frames(media, out_dir, interval, max_frames, duration, times=None, subdir="frames", resize=None, clear_old=True, prefix="frame"):
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
        for old in folder.glob(f"{prefix}_*.jpg"):
            safe_remove(old)
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
        name = f"{prefix}_{idx:04d}_{t:010.3f}.jpg"; target = folder / name
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

def _median(vals):
    vs = sorted(vals); n = len(vs)
    if not n: return 0.0
    mid = n // 2
    return float(vs[mid]) if n % 2 else (vs[mid - 1] + vs[mid]) / 2.0


def plan_boards(quality, scene_cuts, duration, min_len=2.0, max_len=5.0, diff_k=1.5):
    """分镜(board)规划 —— 叙事/拍摄单位，**绝不等同于硬切(hard cut)数量**。

    为什么不能只按硬切分：硬切是「剪辑层」的边界，分镜是「前期叙事 / 拍摄规划层」的单位。
    一镜到底的段落（本片这类运动衔接长镜头）在叙事上依然要按动作节拍、景别·机位·视点变化
    继续拆成多个 board；否则 30s 视频只会产出 1–2 个 20s+ 的巨型板，完全失去规划意义。

    综合信号：
      1) 硬切：真实转场 —— 强制边界
      2) 帧间差异显著点(diff > 中位数 × diff_k)：动作节拍 / 构图转折
      3) 最长板长约束 max_len：即便没检测到变化点，也继续按 diff 降序二分，杜绝超长板
      4) 最短板长约束 min_len：丢弃过碎的候选点
    """
    if not quality: return [], {}
    ts = [q["timestamp_seconds"] for q in quality]
    end = float(duration) if duration else (max(ts) + 1.0)
    hard = {round(float(c), 3) for c in (scene_cuts or [])
            if min_len * 0.5 <= float(c) <= end - min_len * 0.5}
    diffs = [q["diff"] for q in quality[1:]]
    thr = _median(diffs) * diff_k
    beat_pts = []
    for q in quality[1:]:
        t = round(q["timestamp_seconds"], 3)
        if any(abs(t - h) < 0.75 for h in hard): continue   # 该秒已由硬切切开，不重复计
        if q["diff"] > thr: beat_pts.append((t, q["diff"]))
    anchors = [0.0] + sorted(hard) + [round(end, 3)]
    def bisect(a, b, depth=0):
        if b - a <= max_len or depth > 12: return []
        # 可用边界只取「已存在的逐秒帧时刻」：切点必须对齐真实证据帧，而不是任意浮点时间
        internal = [t for t in ts if a + min_len <= t <= b - min_len]
        if not internal: return []
        opts = [(t, s) for (t, s) in beat_pts if a + min_len <= t <= b - min_len]
        if opts:
            t, _ = max(opts, key=lambda x: x[1])          # 有叙事节拍点 -> 用它（最贴近剪辑意图）
        else:
            # 该区间没有显著节拍点：按目标时长等分兜底，绝不留下「因为没有变化点所以不拆」的惰性大板
            nparts = int(math.ceil((b - a) / max_len))
            target = a + (b - a) / nparts
            t = min(internal, key=lambda x: abs(x - target))
        return [round(t, 3)] + bisect(a, t, depth + 1) + bisect(t, b, depth + 1)
    extra = set()
    for i in range(len(anchors) - 1):
        for t in bisect(anchors[i], anchors[i + 1]): extra.add(round(t, 3))
    merged = []
    for t in sorted(set(anchors) | extra):
        if merged and (t - merged[-1]) < min_len and t not in hard:
            continue                                        # 过碎候选：并入前一段
        merged.append(t)
    if merged[-1] < end - 0.05: merged.append(round(end, 3))
    boards = []
    for i in range(len(merged) - 1):
        a, b = merged[i], merged[i + 1]
        boards.append({"board_no": i + 1, "t_start": round(a, 3), "t_end": round(b, 3),
                       "duration": round(b - a, 3),
                       "start_type": "cut" if (i > 0 and a in hard) else ("beat" if i > 0 else "start")})
    return boards, {"diff_threshold": round(thr, 2), "min_board_len": min_len,
                    "max_board_len": max_len, "diff_k": diff_k,
                    "hard_cut_boundaries": len(hard), "beat_candidates": len(beat_pts)}


def pick_representative(quality, t_start, t_end, contrast_gate):
    """为一格 board 选代表帧：先用 contrast 排除黑场/纯色，再取段内 sharpness 最高的帧。

    刻意**不**取「段落第一帧」或「硬切点帧」——那正是黑场淡入、运动转场的高发位置。
    """
    inseg = [q for q in quality if t_start - 1e-6 <= q["timestamp_seconds"] <= t_end + 1e-6]
    if not inseg: return None, 0
    good = [q for q in inseg if q["contrast"] >= contrast_gate]
    rejected = len(inseg) - len(good)
    pool = good if good else inseg
    return max(pool, key=lambda q: q["sharpness"]), rejected


def select_keyframes(out_dir, quality, boards, contrast_gate, long_board=4.0):
    """从 frames/ 逐秒帧中挑选「清晰 + 有内容」的关键姿态帧，复制进 key_frame/。

    与旧的「抽硬切点帧」做法决裂：
      - 硬切点处在运动 / 转场瞬间，恰恰是模糊的高发位置，不能拿来当关键帧；
      - 每格 board 至少 1 张「代表姿态帧」= 段内最清晰且有内容的帧；
      - 较长 board 再补 1 张「起始清晰帧」，体现该段动作的起点状态。
    """
    src_dir = out_dir / "frames"
    kdir = out_dir / "key_frame"; kdir.mkdir(parents=True, exist_ok=True)
    for stale in kdir.glob("keyframe_*.jpg"): safe_remove(stale)
    stats = {"flat_or_black_rejected": 0, "boards": len(boards)}
    picks = []
    for b in boards:
        inseg = [q for q in quality if b["t_start"] - 1e-6 <= q["timestamp_seconds"] <= b["t_end"] + 1e-6]
        good = [q for q in inseg if q["contrast"] >= contrast_gate]
        stats["flat_or_black_rejected"] += len(inseg) - len(good)
        pool = good if good else inseg
        if not pool: continue
        rep = max(pool, key=lambda q: q["sharpness"])
        picks.append((b, rep, "board_representative"))
        if b["duration"] >= long_board:
            mid = b["t_start"] + b["duration"] / 2
            early = [q for q in pool if q["file"] != rep["file"] and q["timestamp_seconds"] <= mid]
            if early:
                picks.append((b, max(early, key=lambda q: q["sharpness"]), "board_opening"))
    items, seen = [], set()
    for b, q, role in picks:
        if q["file"] in seen: continue
        src = src_dir / q["file"]
        if not src.exists(): continue
        dst_name = f"keyframe_b{b['board_no']:02d}_{q['timestamp_seconds']:08.3f}.jpg"
        try:
            shutil.copy2(src, kdir / dst_name)
        except OSError:
            continue
        seen.add(q["file"])
        items.append({"index": 0, "timestamp_seconds": q["timestamp_seconds"],
                      "file": f"key_frame/{dst_name}", "source_frame": q["file"],
                      "board_no": b["board_no"], "board_span": f"{b['t_start']:.2f}-{b['t_end']:.2f}s",
                      "role": role, "sharpness": q["sharpness"], "contrast": q["contrast"]})
    # 按「镜格 → 时间」排序后统一编号，保证清单顺序与影片顺序一致（否则会出现
    # board_representative 排在 board_opening 之前这类时间倒挂，读起来像乱排）
    items.sort(key=lambda x: (x["board_no"], x["timestamp_seconds"]))
    for i, it in enumerate(items, start=1): it["index"] = i
    stats["keyframe_count"] = len(items)
    return items, stats


def build_story_board(out_dir, story_board_dir, boards, everysec, plan_info=None):
    """Generate story_board/story_board.md (Obsidian-friendly) and story_board/story_board.html
    (visual board). 每格 board = 一则叙事/拍摄面板：段内「最清晰且有内容」的代表帧 + [待填]
    注解字段（景别/机位/运动/关键动作/对白音效）。write-if-missing so user edits survive a re-run.

    两条刻意为之的原则：
      - board 是叙事规划单位，**不等于硬切数**；一镜到底段落按动作节拍与景别/机位/视点变化继续拆格。
      - 代表帧取段内 sharpness 最高者，而非段落首帧或硬切点帧——后两者常是黑场淡入或运动转场糊帧。
    """
    story_board_dir.mkdir(parents=True, exist_ok=True)
    md_path = story_board_dir / "story_board.md"
    html_path = story_board_dir / "story_board.html"
    dur_total = round(max((b["t_end"] for b in boards), default=0.0), 1)
    tag = {"cut": "硬切起始", "beat": "节拍转折", "start": "开片"}.get
    def emb(rep):
        if not rep: return None
        return "../" + rep  # rep like "frames/..."; story_board 与它同级
    def secs_in(board):
        return [f["filename"] for f in everysec
                if board["t_start"] - 1e-6 <= f["timestamp_seconds"] <= board["t_end"] + 1e-6]
    if not md_path.exists():
        md = ["# 分镜板 Storyboard（叙事/拍摄规划单位 · 构图/机位/运镜/动作/对白音效）\n",
              f"> 自动生成骨架；共 {len(boards)} 格，总时长约 {dur_total}s。注解字段待「看帧」后回填。\n",
              "> 代表帧 = 该格区间内 **清晰度最高且有画面内容** 的逐秒帧（已排除黑场/纯色与运动模糊帧），刻意不取段落首帧或硬切点帧。\n",
              "> 分镜不等于硬切数：一镜到底的段落按动作节拍与景别·机位·视点变化继续拆格。\n"]
        if plan_info:
            md.append(f"> 规划参数：单格 {plan_info['min_board_len']}–{plan_info['max_board_len']}s，"
                      f"帧间差异阈值 {plan_info['diff_threshold']}（中位数×{plan_info['diff_k']}），"
                      f"硬切边界 {plan_info['hard_cut_boundaries']} 处，节拍候选 {plan_info['beat_candidates']} 个。\n")
        md += ["\n## 分镜总览\n",
               "| 镜号 | 时间区间 | 时长 | 起始方式 | 代表帧（清晰度） |",
               "|---|---|---|---|---|"]
        for b in boards:
            q = b.get("rep"); line = (f"| {b['board_no']} | {b['t_start']:.2f}–{b['t_end']:.2f}s "
                                      f"| {b['duration']}s | {tag(b['start_type'])} |")
            if q and b.get("rep_image"):
                md.append(f"{line} `{emb(b['rep_image'])}`（{q['sharpness']:.0f}） |")
            else:
                md.append(f"{line} — |")
        md.append("\n## 逐格注解（待填）\n")
        for b in boards:
            rep = emb(b.get("rep_image"))
            md.append(f"\n### 镜 {b['board_no']}（{b['t_start']:.2f}–{b['t_end']:.2f}s · {b['duration']}s · {tag(b['start_type'])}）\n")
            if rep: md.append(f"![代表帧]({rep})\n")
            md.append("| 字段 | 内容（待填） |\n|---|---|")
            md.append("| 景别 | `[待填]` |")
            md.append("| 机位 | `[待填]` |")
            md.append("| 运动 | `[待填]` |")
            md.append("| 关键动作 | `[待填]` |")
            md.append("| 对白/音效 | `[待填]` |")
            secs = secs_in(b)
            if secs:
                shown = secs[:8]; more = "" if len(secs) <= 8 else f" …（共 {len(secs)} 帧）"
                md.append(f"\n> 逐秒参考帧：{', '.join(shown)}{more}（位于 `frames/`）\n")
        md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    if not html_path.exists():
        cards = []
        for b in boards:
            rep = emb(b.get("rep_image"))
            alt = f"board {b['board_no']}"
            img = f'<img src="{rep}" alt="{alt}">' if rep else '<div class="noimg">无代表帧</div>'
            q = b.get("rep")
            sub = f" · {tag(b['start_type'])}"
            if q: sub += f" · 清晰度 {q['sharpness']:.0f}"
            cards.append(
                f'<div class="panel">{img}<div class="meta">'
                f'<h3>镜 {b["board_no"]} · {b["t_start"]:.2f}–{b["t_end"]:.2f}s · {b["duration"]}s{sub}</h3>'
                f'<table>'
                f'<tr><td class="k">景别</td><td class="todo">待填</td></tr>'
                f'<tr><td class="k">机位</td><td class="todo">待填</td></tr>'
                f'<tr><td class="k">运动</td><td class="todo">待填</td></tr>'
                f'<tr><td class="k">关键动作</td><td class="todo">待填</td></tr>'
                f'<tr><td class="k">对白/音效</td><td class="todo">待填</td></tr>'
                f'</table></div></div>')
        html = (
            '<!doctype html><html lang="zh"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>分镜板 Storyboard · {len(boards)} 格</title>'
            '<style>'
            'body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,"PingFang SC","Microsoft YaHei",sans-serif;'
            'margin:0;background:#f4f4f5;color:#1f1f1f}'
            'header{padding:16px 24px;background:#1f2330;color:#fff}'
            'header h1{margin:0;font-size:18px}header p{margin:4px 0 0;font-size:13px;color:#b9c0d0}'
            '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;padding:16px}'
            '.panel{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 5px rgba(0,0,0,.12)}'
            '.panel img{width:100%;display:block;background:#000;max-height:240px;object-fit:contain}'
            '.noimg{height:180px;display:flex;align-items:center;justify-content:center;background:#222;color:#888}'
            '.meta{padding:10px 12px}.meta h3{margin:0 0 8px;font-size:14px}'
            'table{width:100%;border-collapse:collapse;font-size:12px}'
            'td{border:1px solid #ececec;padding:5px 7px;vertical-align:top}'
            'td.k{background:#f7f7f9;width:60px;color:#666;font-weight:600}'
            '.todo{color:#c0392b;font-style:italic}</style></head><body>'
            f'<header><h1>分镜板 Storyboard</h1><p>共 {len(boards)} 格 · 总时长约 {dur_total}s'
            f' · 代表帧取各格最清晰且有内容的帧（frames/）· 分镜不等于硬切数</p></header>'
            '<div class="grid">' + "".join(cards) + '</div></body></html>')
        html_path.write_text(html, encoding="utf-8")
    return ("story_board/story_board.md" if md_path.exists() else None,
            "story_board/story_board.html" if html_path.exists() else None)

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
    ap.add_argument("--scene-cuts", action="store_true", help="（保留兼容）场景切点始终自动检测，并生成 key_frame/ 关键帧与 story_board/ 分镜板；此开关无额外效果。用 --cut-threshold 调灵敏度。")
    ap.add_argument("--cut-threshold", type=float, default=10.0, help="scdet sensitivity on a 0-100 scale; higher = fewer cuts. Detected cuts are used only as FORCED story-board boundaries, never to pick keyframes.")
    ap.add_argument("--board-min", type=float, default=2.0, help="最短分镜格时长(秒)；更碎的节拍候选会被并入相邻格，避免把连续动作切散。")
    ap.add_argument("--board-max", type=float, default=5.0, help="最长分镜格时长(秒)；即使没检测到视觉变化点，超长格也会按帧间差异降序继续二分，杜绝 20s+ 巨型格。")
    ap.add_argument("--board-diff-k", type=float, default=1.5, help="节拍候选阈值倍数：帧间差异 > 中位数×此值 即视为一处叙事转折候选。调低更敏感、拆得更细。")
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
    # 场景切点检测（始终运行）：仅作为分镜的「强制边界」信号之一，不再是唯一的镜头定义
    scene_cuts, sc_err = detect_scene_cuts(media, args.cut_threshold, 0)
    # 过滤极短/片头伪切点（scdet 常在 t≈0 误报），避免生成 ~0 时长的退化边界
    MIN_CUT_GAP = 0.5
    if scene_cuts:
        _f = []
        for _t in scene_cuts:
            if _t < MIN_CUT_GAP: continue
            if _f and _t - _f[-1] < MIN_CUT_GAP: continue
            _f.append(_t)
        scene_cuts = _f
    if sc_err:
        notes.append("Scene-cut detection failed: " + sc_err)
    frames = everysec  # bundle.frames = 逐秒帧全量证据（向后兼容 make_sheets 读取）
    # ---- 帧级视觉评估：清晰度 / 对比度(排除黑场与纯色) / 帧间差异 ----
    quality = analyze_series([(f["timestamp_seconds"], out / Path(f["filename"])) for f in everysec]) if everysec else []
    _contrasts = [q["contrast"] for q in quality] or [0.0]
    contrast_gate = max(12.0, _median(_contrasts) * 0.35)  # 低于此值视为黑场/纯色等无信息画面
    # ---- 分镜(board)规划：叙事/拍摄单位，绝不等于硬切数 ----
    boards, plan_info = plan_boards(quality, scene_cuts, duration,
                                    min_len=args.board_min, max_len=args.board_max, diff_k=args.board_diff_k)
    plan_info["contrast_gate"] = round(contrast_gate, 1)
    # 每格代表帧 = 段内「有内容且最清晰」的帧。刻意不取段落首帧/硬切点帧：那是黑场淡入与运动模糊的高发位置。
    for b in boards:
        rep, _rej = pick_representative(quality, b["t_start"], b["t_end"], contrast_gate)
        b["rep"] = rep
        b["rep_image"] = ("frames/" + rep["file"]) if rep else None
    shot_count = len(boards)
    # ---- 关键帧：不再抽硬切点帧，改为按清晰度从逐秒帧里筛选「关键姿态帧」 ----
    key_frame_dir = out / "key_frame"; key_frame_dir.mkdir(parents=True, exist_ok=True)
    kf_items, kf_stats = select_keyframes(out, quality, boards, contrast_gate)
    print(json.dumps({"scene_cuts_detected": len(scene_cuts), "boards": len(boards),
                      "keyframes_selected": len(kf_items), "contrast_gate": round(contrast_gate, 1),
                      "plan": plan_info}, ensure_ascii=False))
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
    notes.append(f"关键帧已写入 key_frame/（{len(kf_items)} 张，按清晰度从逐秒帧筛选的代表姿态帧；"
                 f"已按对比度排除黑场/纯色候选 {kf_stats.get('flat_or_black_rejected', 0)} 帧）；"
                 f"分镜板已写入 story_board/（{shot_count} 格，代表帧取各格最清晰帧；"
                 f"分镜按叙事节拍+时长约束拆分，不等于硬切数）。")
    if frame_error: notes.append("Frame extraction issue: " + frame_error)
    if audio_error: notes.append("Audio extraction note: " + audio_error)

    # ---- sheets 证据包：分页小图 + 节奏实录 + 动作模板（均 write-if-missing，重跑不覆盖已填） ----
    pages = make_sheets(out, sheets_dir, everysec)
    if not pages:
        notes.append("分页缩略图未能生成（Pillow 缺失或无逐秒帧）。请安装 Pillow 或直接读 frames/ 单帧后填写。")
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
            section_lines.append("\n> 未生成分页缩略图（Pillow 缺失或无可读帧）。请直接阅读 frames/ 单帧后填写。")
        (sheets_dir / "动作模板.md").write_text("\n".join(section_lines) + "\n", encoding="utf-8")

    # ---- key_frame 关键帧清单 + story_board 分镜板（见 build_story_board） ----
    keyframe_manifest = None
    story_md = story_html = None
    kf_list = kf_items
    manifest = {"schema": "keyframe-manifest-v2",
                "selection": "清晰度筛选 + 段内代表姿态（已废弃『抽硬切点帧』：切点处于运动/转场瞬间，是运动模糊的高发位置）",
                "cut_threshold_for_boundaries": args.cut_threshold,
                "contrast_gate": round(contrast_gate, 1),
                "plan": plan_info, "stats": kf_stats,
                "keyframe_count": len(kf_items), "keyframes": kf_list}
    manifest["note"] = ("每个关键帧是某格分镜(board)内『清晰度最高且有画面内容』的姿态帧；"
                        "已按 contrast 排除黑场/纯色帧，并按 sharpness 规避运动模糊帧。")
    write_json(key_frame_dir / "key_frame_manifest.json", manifest)
    keyframe_manifest = "key_frame/key_frame_manifest.json"
    mlines = ["# 关键帧清单 Keyframe Manifest\n",
              f"> 共 {len(kf_items)} 个关键帧；筛选口径：每格分镜内 **清晰度最高且有内容** 的帧。\n",
              f"> 被判为黑场/纯色而排除的候选 {kf_stats.get('flat_or_black_rejected', 0)} 帧（对比度低于 {contrast_gate:.1f}）；"
              f"硬切阈值(scdet 0–100) {args.cut_threshold} 仅用于分镜强制边界，不再用来抽关键帧。\n",
              "> role：board_representative = 该格代表姿态帧；board_opening = 较长板的起始清晰帧。\n",
              "| # | 时间 | 所属镜格 | 区间 | 角色 | 清晰度 | 对比度 | 文件 |",
              "|---|---|---|---|---|---|---|---|"]
    for k in kf_list:
        role = "代表姿态" if k["role"] == "board_representative" else "起始清晰"
        mlines.append(f"| {k['index']} | {k['timestamp_seconds']:.3f}s | 镜{k['board_no']} | {k['board_span']} "
                      f"| {role} | {k['sharpness']:.0f} | {k['contrast']:.0f} | `{k['file']}` |")
    if not kf_list:
        mlines.append("| — | — | — | — | — | — | — | 无（见上方 note） |")
    (key_frame_dir / "key_frame_manifest.md").write_text("\n".join(mlines) + "\n", encoding="utf-8")
    story_md, story_html = build_story_board(out, out / "story_board", boards, everysec, plan_info)

    file_map = {"media_file":str(media),"compressed_archive":contact,"per_second_frames_dir":"frames",
                "keyframe_dir":"key_frame","keyframe_manifest":keyframe_manifest,
                "story_board_dir":"story_board","story_board_md":story_md,"story_board_html":story_html,
                "board_count":len(boards),"shot_count":shot_count,"audio":audio,"sheets_dir":"sheets","roles_dir":"roles",
                "action_template":action_template,"rhythm_record":"sheets/节奏实录.md",
                "cuts_list":cuts_file,"reference_audio":ref_audio,
                "sheet_pages":[p["file"] for p in pages],"keyframe_count":len(kf_items),"per_second_count":len(everysec)}
    if transcript and transcript.get("ok"): file_map.update({"transcript_text":"transcript.txt","transcript_json":"transcript.json"})
    bundle = {"schema_version":SCHEMA,"status":"ok" if everysec else "partial","source":source,"media":media_info,
              "extraction":{"sampling_interval_seconds":args.interval,"max_frames":args.max_frames,"per_second_count":len(everysec),
                            "board_count":len(boards),"shot_count":shot_count,
                            "board_min_len":args.board_min,"board_max_len":args.board_max,"board_diff_k":args.board_diff_k,
                            "contrast_gate":round(contrast_gate,1),"plan":plan_info,
                            "keyframe_count":len(kf_items),"scene_cut_mode":bool(args.scene_cuts),
                            "scene_cuts":len(scene_cuts) if scene_cuts else None,"cut_threshold":args.cut_threshold,
                            "avg_beats_per_second":avg_bps,"audio_extracted":bool(audio),"transcription_requested":args.transcribe,"transcription":transcript},
              "frames":everysec,"files":file_map,"notes":notes,"elapsed_seconds":round(time.time()-started,2)}
    write_json(out / "analysis_bundle.json", bundle)
    print(json.dumps({"status":bundle["status"],"out_dir":str(out),"per_second_count":len(everysec),"keyframe_count":len(kf_items),
                      "board_count":len(boards),"scene_cuts":len(scene_cuts) if scene_cuts else None,"avg_beats_per_second":avg_bps,
                      "contrast_gate":round(contrast_gate,1),"plan":plan_info,
                      "compressed_archive":contact,"sheets_pages":len(pages),"rhythm_record":"sheets/节奏实录.md",
                      "action_template":action_template,"story_board_md":story_md,"story_board_html":story_html,
                      "keyframe_manifest":keyframe_manifest,"audio_extracted":bool(audio),"bundle":str(out/"analysis_bundle.json"),"notes":notes}, ensure_ascii=False, indent=2))
    return 0 if everysec else 4

if __name__ == "__main__": raise SystemExit(main())
