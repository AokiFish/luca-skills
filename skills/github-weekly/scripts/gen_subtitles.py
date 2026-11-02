#!/usr/bin/env python3
"""从 data.ts + GithubWeekly.tsx 抽取文案与分镜时长，生成 SRT / VTT 字幕。

不依赖配音文件：字幕按分镜（CUTS）的固定时段对齐，因此无论是否有配音都能产出。
每个场景对应屏幕底部 SubtitleBar 的文案：封面 1 段 + 每个项目 intro/detail 2 段 + 片尾 1 段。

用法：
    python gen_subtitles.py --data src/GithubWeekly/data.ts \
        --tsx src/GithubWeekly/GithubWeekly.tsx --outdir out/github-weekly-YYYY-MM-DD

输出：subtitles.srt / subtitles.vtt
"""
import argparse
import os
import re


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_week_word(src):
    m = re.search(r'export const WEEK_WORD\s*=\s*"([^"]*)"', src)
    return m.group(1) if m else "本周"


def extract_week_stars(src):
    return [int(x) for x in re.findall(r"weekStars:\s*(\d+)", src)]


def extract_intros_details(src):
    intros = re.findall(r'subtitleIntro:\s*"([^"]*)"', src)
    details = re.findall(r'subtitleDetail:\s*"([^"]*)"', src)
    return intros, details


def extract_cuts(tsx):
    m = re.search(r"const CUTS\s*=\s*\{(.*?)\};", tsx, re.S)
    block = m.group(1) if m else ""
    keys = [
        "coverEnd", "p1IntroEnd", "p1End", "p2IntroEnd", "p2End",
        "p3IntroEnd", "p3End", "p4IntroEnd", "p4End", "p5IntroEnd", "p5End",
    ]
    cuts = {}
    for k in keys:
        mm = re.search(rf"{k}:\s*(\d+)", block)
        cuts[k] = int(mm.group(1)) if mm else 0
    dm = re.search(r"GITHUB_WEEKLY_DURATION\s*=\s*(\d+)", tsx)
    dur = int(dm.group(1)) if dm else 0
    return cuts, dur


def build_segments(week_word, week_stars, intros, details, cuts, dur, n):
    new_stars = sum(week_stars)
    segs = []
    segs.append(
        (
            0,
            cuts["coverEnd"],
            f"{week_word} GitHub 周榜出炉，{n} 个项目一周狂揽 {new_stars:,} 颗星。",
        )
    )
    pairs = [
        ("p1IntroEnd", "p1End"),
        ("p2IntroEnd", "p2End"),
        ("p3IntroEnd", "p3End"),
        ("p4IntroEnd", "p4End"),
        ("p5IntroEnd", "p5End"),
    ]
    prev = cuts["coverEnd"]
    for i, (end_key, next_key) in enumerate(pairs):
        segs.append((prev, cuts[end_key], intros[i]))
        segs.append((cuts[end_key], cuts[next_key], details[i]))
        prev = cuts[next_key]
    segs.append(
        (cuts["p5End"], dur, f"{week_word} GitHub 周榜收官，下周同一时间见。")
    )
    return segs


def to_srt_time(frames, fps):
    s = frames / fps
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s * 1000) % 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def write_srt(segs, fps, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(segs, 1):
            f.write(f"{i}\n{to_srt_time(a, fps)} --> {to_srt_time(b, fps)}\n{t}\n\n")


def write_vtt(segs, fps, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for i, (a, b, t) in enumerate(segs, 1):
            sa = to_srt_time(a, fps).replace(",", ".")
            sb = to_srt_time(b, fps).replace(",", ".")
            f.write(f"{i}\n{sa} --> {sb}\n{t}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="data.ts 路径")
    ap.add_argument("--tsx", required=True, help="GithubWeekly.tsx 路径")
    ap.add_argument("--outdir", required=True, help="输出目录")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    dsrc = read(a.data)
    tsrc = read(a.tsx)
    week_word = extract_week_word(dsrc)
    week_stars = extract_week_stars(dsrc)
    intros, details = extract_intros_details(dsrc)
    cuts, dur = extract_cuts(tsrc)
    n = len(intros)
    segs = build_segments(week_word, week_stars, intros, details, cuts, dur, n)

    os.makedirs(a.outdir, exist_ok=True)
    write_srt(segs, a.fps, os.path.join(a.outdir, "subtitles.srt"))
    write_vtt(segs, a.fps, os.path.join(a.outdir, "subtitles.vtt"))
    print(f"字幕已生成 {len(segs)} 段 -> subtitles.srt / subtitles.vtt (fps={a.fps})")


if __name__ == "__main__":
    main()
