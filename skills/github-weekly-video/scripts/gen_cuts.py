#!/usr/bin/env python3
"""把配音对齐到分镜：silencedetect 检测停顿 + 解说词字数比例 → 回写 CUTS/DURATION/VO_FILE。

核心思路：
  配音是「一整段连续旁白」，视频分镜是「封面 + 5×(项目过场/详解) + 片尾」。
  这段脚本做三件事：
  1. 用 ffmpeg silencedetect 找出旁白里真正的停顿点（句间换气/场景切换）。
  2. 读解说词 narration.txt（每行 = 一个场景的台词，共 12 行：封面、
     p1 intro、p1 detail、…、p5 intro、p5 detail、片尾），按累计字数比例
     在「人声起止区间」内给每个场景边界估一个时间点。
  3. 把每个边界「就近吸附」到最近的停顿点，保证切换落在真人换气处而不是
     念到一半被硬切；然后把秒换算成帧，回写 GithubWeekly.tsx 的 CUTS 与
     GITHUB_WEEKLY_DURATION，以及 data.ts 的 VO_FILE。

用法：
    python gen_cuts.py --vo public/vo/vo-full.mp3 \
        --narration narration.txt \
        --tsx src/GithubWeekly/GithubWeekly.tsx \
        --data src/GithubWeekly/data.ts \
        --fps 30 [--silence-db -35] [--min-pause 0.25] [--tail-frames 36]

输出：改好 CUTS / GITHUB_WEEKLY_DURATION 的 GithubWeekly.tsx，
      改好 VO_FILE 的 data.ts，并在 stdout 打印每个场景的起止帧。
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

# CUTS 的 key，正好对应 12 个场景之间的 11 个内部边界。
CUT_KEYS = [
    "coverEnd", "p1IntroEnd", "p1End", "p2IntroEnd", "p2End",
    "p3IntroEnd", "p3End", "p4IntroEnd", "p4End", "p5IntroEnd", "p5End",
]


def silence_gaps(vo_path, silence_db, min_pause):
    """跑 ffmpeg silencedetect，返回 (speech_start, speech_end, pauses[])。

    pauses = [(start, end, mid), ...] 均为秒；pauses 里的停顿时长 >= min_pause。
    speech_start 是人声实际起始；speech_end 是人声实际结束（排除首尾静音）。
    """
    cmd = [
        "ffmpeg", "-i", vo_path,
        "-af", f"silencedetect=noise={silence_db}dB:d={min_pause}",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg silencedetect 失败: {r.stderr[-800:]}")
    starts = [
        float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", r.stderr)
    ]
    ends = [
        float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", r.stderr)
    ]
    # 时长（作为 speech_end 兜底）
    dur = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

    pauses = []
    for s, e in zip(starts, ends):
        if e - s >= min_pause:
            pauses.append((s, e, (s + e) / 2))

    # speech_start：第一段静音结束；speech_end：最后一段静音开始
    speech_start = ends[0] if ends and starts and starts[0] < 1.0 else 0.0
    speech_start = max(speech_start, 0.0)
    speech_end = starts[-1] if starts else dur
    if dur and speech_end > dur:
        speech_end = dur
    return speech_start, speech_end, pauses


def read_narration(path):
    lines = [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip()]
    if len(lines) < 12:
        sys.exit(
            f"narration 需要 ≥12 行（封面 + 5×(intro/detail) + 片尾），当前 {len(lines)} 行"
        )
    return lines[:12]


def snap(target, pauses, window):
    """把 target（秒）吸附到 window 范围内最近的停顿中点；没有则原样返回。"""
    best, best_d = target, abs(window) + 1
    for s, e, mid in pauses:
        if target - window <= mid <= target + window:
            d = abs(target - mid)
            if d < best_d:
                best, best_d = mid, d
    return best


def compute_cuts(segments, speech_start, speech_end, pauses, fps, tail_frames):
    """按累计字数比例 + 就近吸附停顿，算出 11 个边界（帧）与总时长（帧）。"""
    weights = [len(s) for s in segments]
    total = sum(weights)
    span = speech_end - speech_start
    if span <= 0:
        sys.exit("人声区间为空，无法对齐")

    # 先按字数比例估边界（秒）
    fracs, acc = [], 0
    for i in range(len(segments) - 1):
        acc += weights[i]
        fracs.append(acc / total)

    window = 0.8  # 秒：边界允许吸附到停顿的范围
    bounds = [speech_start + span * f for f in fracs]
    snapped = [snap(b, pauses, window) for b in bounds]

    # 单调性保证：每个边界至少比上一个多 min_seg 帧
    min_seg = int(fps * 0.6)
    frames = []
    prev = int(round(speech_start * fps))
    for b in snapped:
        f = int(round(b * fps))
        if f < prev + min_seg:
            f = prev + min_seg
        prev = f
        frames.append(f)

    duration = int(round(speech_end * fps)) + tail_frames
    # 最后一个边界(片尾开始)必须 < duration
    if frames[-1] >= duration:
        frames[-1] = duration - min_seg
    return dict(zip(CUT_KEYS, frames)), duration


def write_tsx(tsx_path, cuts, duration):
    s = open(tsx_path, encoding="utf-8").read()
    # 重写 CUTS 块
    block = "\n  ".join([f"{k}: {v}," for k, v in cuts.items()])
    s = re.sub(
        r"const CUTS\s*=\s*\{(.*?)\};",
        "const CUTS = {\n  " + block + "\n};",
        s,
        flags=re.S,
    )
    # 重写总时长
    s = re.sub(
        r"export const GITHUB_WEEKLY_DURATION\s*=\s*\d+;",
        f"export const GITHUB_WEEKLY_DURATION = {duration};",
        s,
    )
    open(tsx_path, "w", encoding="utf-8").write(s)


def write_vo_file(data_path, vo_rel):
    s = open(data_path, encoding="utf-8").read()
    s = re.sub(
        r'export const VO_FILE\s*=\s*"[^"]*"',
        f'export const VO_FILE = "{vo_rel}"',
        s,
    )
    open(data_path, "w", encoding="utf-8").write(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", required=True, help="配音文件（wav/mp3）绝对或相对路径")
    ap.add_argument("--narration", required=True, help="解说词文件，每行一个场景，共12行")
    ap.add_argument("--tsx", required=True, help="GithubWeekly.tsx 路径")
    ap.add_argument("--data", required=True, help="data.ts 路径")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--vo-rel", default="", help="VO_FILE 写入的相对路径，如 vo/vo-full.mp3；缺省用 --vo 相对项目根")
    ap.add_argument("--silence-db", type=float, default=-35)
    ap.add_argument("--min-pause", type=float, default=0.25)
    ap.add_argument("--tail-frames", type=int, default=36, help="片尾余量帧数（配音结束后留的静音）")
    a = ap.parse_args()

    speech_start, speech_end, pauses = silence_gaps(
        a.vo, a.silence_db, a.min_pause
    )
    segments = read_narration(a.narration)

    cuts, duration = compute_cuts(
        segments, speech_start, speech_end, pauses, a.fps, a.tail_frames
    )

    vo_rel = a.vo_rel or a.vo.replace("\\", "/").lstrip("./")
    write_tsx(a.tsx, cuts, duration)
    write_vo_file(a.data, vo_rel)

    print(f"配音: {os.path.abspath(a.vo)}  (人声 {speech_start:.2f}s → {speech_end:.2f}s)")
    print(f"停顿点 {len(pauses)} 处; 总时长 {duration} 帧 / {duration/a.fps:.1f}s @ {a.fps}fps\n")
    for k, v in cuts.items():
        print(f"  {k:12s} = {v:6d}  ({v/a.fps:6.2f}s)")
    print("\n已回写:", os.path.abspath(a.tsx))
    print("已回写 VO_FILE:", os.path.abspath(a.data))


if __name__ == "__main__":
    main()
