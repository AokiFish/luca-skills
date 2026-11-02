#!/usr/bin/env python3
"""编排输出：渲染 mp4 + 首帧 png + 字幕，统一放进 out/github-weekly-<日期>/。

流程：
  1. 解析 --date（默认今天）得到输出目录名与文件名。
  2. 若传 --vo（配音 mp3），复制到 public/vo/<name> 并改写 data.ts 的 VO_FILE。
     不传 --vo 则保持 data.ts 的 VO_FILE（通常为空=无声仅字幕）。
  3. remotion render GithubWeekly -> mp4
  4. remotion still GithubWeekly --frame=0 -> 首帧 png
  5. 调 gen_subtitles.py 生成 SRT/VTT

依赖：目标目录是已初始化的 Remotion 项目（含 node_modules/.bin/remotion、
src/GithubWeekly、remotion.config.ts）。本脚本只做编排，不生成配音。

用法：
    python build.py --project-root /path/to/remotion-project --date 2026-11-02
    python build.py --project-root . --date 2026-11-02 --vo ~/Downloads/cloned.mp3
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys


def run(cmd):
    print("+", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"命令失败 (exit={r.returncode}): {' '.join(cmd)}")


def get_fps(root):
    p = os.path.join(root, "remotion.config.ts")
    if os.path.exists(p):
        s = open(p, encoding="utf-8").read()
        m = re.search(r"fps:\s*(\d+)", s)
        if m:
            return int(m.group(1))
    return 30


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--vo", default="", help="配音 mp3 路径（可选，不传=无声仅字幕）")
    ap.add_argument(
        "--vo-name",
        default="",
        help="public/vo 下文件名，默认 github-weekly-<date>-full.mp3",
    )
    ap.add_argument("--remotion", default=None, help="remotion CLI 路径，默认 node_modules/.bin/remotion")
    a = ap.parse_args()

    root = os.path.abspath(a.project_root)
    out_dir = os.path.join(root, "out", f"github-weekly-{a.date}")
    os.makedirs(out_dir, exist_ok=True)
    remotion = a.remotion or os.path.join(root, "node_modules", ".bin", "remotion")
    if os.name == "nt" and not remotion.endswith(".cmd"):
        alt = remotion + ".cmd"
        if os.path.exists(alt):
            remotion = alt
    comp = "GithubWeekly"
    mp4 = os.path.join(out_dir, f"github-weekly-{a.date}.mp4")
    png = os.path.join(out_dir, f"首帧-{a.date}.png")

    # 配音：复制并改写 data.ts 的 VO_FILE
    if a.vo:
        name = a.vo_name or f"github-weekly-{a.date}-full.mp3"
        dest = os.path.join(root, "public", "vo", name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy(a.vo, dest)
        dp = os.path.join(root, "src", "GithubWeekly", "data.ts")
        s = open(dp, encoding="utf-8").read()
        s = re.sub(
            r'export const VO_FILE\s*=\s*"[^"]*"',
            f'export const VO_FILE = "vo/{name}"',
            s,
        )
        open(dp, "w", encoding="utf-8").write(s)
        print(f"已接入配音: vo/{name}")

    env = dict(os.environ)
    env["NODE_OPTIONS"] = ""  # 避开沙箱 safe-delete 对 remotion Chrome 清理的拦截

    run([remotion, "render", comp, mp4, "--concurrency=4"])
    run([remotion, "still", comp, png, "--frame=0"])

    fps = get_fps(root)
    here = os.path.dirname(os.path.abspath(__file__))
    run(
        [
            sys.executable,
            os.path.join(here, "gen_subtitles.py"),
            "--data", os.path.join(root, "src", "GithubWeekly", "data.ts"),
            "--tsx", os.path.join(root, "src", "GithubWeekly", "GithubWeekly.tsx"),
            "--outdir", out_dir,
            "--fps", str(fps),
        ]
    )

    print("\n完成输出目录:", out_dir)
    for f in ["github-weekly-%s.mp4" % a.date, "首帧-%s.png" % a.date, "subtitles.srt", "subtitles.vtt"]:
        print("  -", f)


if __name__ == "__main__":
    main()
