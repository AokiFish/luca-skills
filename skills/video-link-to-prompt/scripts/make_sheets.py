#!/usr/bin/env python3
"""Build paginated contact sheets from extracted frames into <out>/sheets/.

This is the dense-evidence companion to analyze_video.py: instead of one giant
overview image, it lays frames out into readable pages (default 5x9 = 45/page)
so the host agent can read each page and log action beats without missing cuts.

Run standalone:
    python scripts/make_sheets.py --out ./video-analysis
Or import `make_sheets` from analyze_video.py (called automatically there).
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path


def make_sheets(out_dir, sheets_dir, frames, cols=5, rows=9, thumb=(300, 180), quality=88):
    """Render paginated contact sheets. Returns list of page dicts.

    frames: list of records with keys 'filename' (relative to out_dir) and
            'timestamp_seconds'. Pages are written to sheets_dir/sheet_XX.jpg.
            Returns [] if PIL is unavailable or no frames.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return []
    out_dir = Path(out_dir).resolve(); sheets_dir = Path(sheets_dir).resolve()
    sheets_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for fr in frames:
        try:
            im = Image.open(out_dir / fr["filename"]).convert("RGB")
            im.thumbnail(thumb)
            items.append((im, str(fr.get("timestamp_seconds", "")), fr.get("timestamp_seconds", 0)))
        except Exception:
            pass
    if not items:
        return []
    items.sort(key=lambda t: t[2])
    per_page = cols * rows
    pages = []
    font = None
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    for pi in range(0, len(items), per_page):
        chunk = items[pi:pi + per_page]
        grid_w = cols * (thumb[0] + 16)
        grid_h = rows * (thumb[1] + 28)
        sheet = Image.new("RGB", (grid_w, grid_h), "white")
        draw = ImageDraw.Draw(sheet)
        for j, (im, label, _) in enumerate(chunk):
            cx = (j % cols) * (thumb[0] + 16) + 8
            cy = (j // cols) * (thumb[1] + 28) + 8
            sheet.paste(im, (cx + (thumb[0] - im.width) // 2, cy + (thumb[1] - im.height) // 2))
            draw.rectangle([cx, cy, cx + thumb[0], cy + thumb[1]], outline=(200, 200, 200))
            if font:
                draw.text((cx + 2, cy + thumb[1] + 4), f"{label}s", fill="black", font=font)
        name = f"sheet_{len(pages) + 1:02d}.jpg"
        sheet.save(sheets_dir / name, quality=quality)
        t_start = chunk[0][2]; t_end = chunk[-1][2]
        pages.append({"file": f"sheets/{name}", "t_start": round(float(t_start), 2),
                      "t_end": round(float(t_end), 2), "count": len(chunk)})
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="Analysis output dir (contains frames/)")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--rows", type=int, default=9)
    args = ap.parse_args()
    out = Path(args.out).expanduser().resolve()
    bundle_path = out / "analysis_bundle.json"
    frames = []
    if bundle_path.exists():
        import json
        try:
            frames = json.loads(bundle_path.read_text(encoding="utf-8")).get("frames", [])
        except Exception:
            frames = []
    if not frames:
        fdir = out / "frames"
        if fdir.exists():
            import re
            for p in sorted(fdir.glob("*.jpg")):
                m = re.search(r"_(\d+\.\d+)\.jpg$", p.name)
                ts = float(m.group(1)) if m else 0.0
                frames.append({"filename": f"frames/{p.name}", "timestamp_seconds": ts})
    pages = make_sheets(out, out / "sheets", frames, cols=args.cols, rows=args.rows)
    print(json.dumps({"sheets_dir": str(out / "sheets"), "pages": len(pages),
                      "ranges": [[p["t_start"], p["t_end"]] for p in pages]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
