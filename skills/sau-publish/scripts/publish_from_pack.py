#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 video-publish-pack 内容包生成 sau 发布命令；加 --execute 则直接执行。

用法（在项目根或任意目录）:
    python scripts/publish_from_pack.py --pack <content-pack.json> --platform douyin --account mimi
    python scripts/publish_from_pack.py --pack <content-pack.json> --platform douyin --account mimi --execute

默认 dry-run，只打印将要执行的命令，不发布。
"""

import argparse
import json
import os
import shlex
import subprocess
import sys

# platform 参数 -> (内容包字段前缀, sau 子命令)
PLATFORMS = {
    "douyin": ("douyin", ["douyin", "upload-video"]),
    "xiaohongshu": ("xhs", ["xiaohongshu", "upload-video"]),
    "xhs": ("xhs", ["xiaohongshu", "upload-video"]),
    "bilibili": ("bilibili", ["bilibili", "upload-video"]),
    "kuaishou": ("kuaishou", ["kuaishou", "upload-video"]),
    "tencent": ("tencent", ["tencent", "upload-video"]),
    "baijiahao": ("baijiahao", ["baijiahao", "upload-video"]),
    "weibo": ("weibo", ["weibo", "upload-video"]),
    "hupu": ("hupu", ["hupu", "upload-video"]),
    "zhihu": ("zhihu", ["zhihu", "upload-video"]),
    "youtube": ("youtube", ["youtube", "upload-video"]),
    "alipay": ("alipay", ["alipay", "upload-video"]),
    "dayu": ("dayu", ["dayu", "upload-video"]),
}

CAPTION_PLATFORMS = {"tiktok", "instagram"}


def find_sau(project):
    for rel in (r".venv\Scripts\sau.exe", r".venv\Scripts\sau"):
        p = os.path.join(project, rel)
        if os.path.exists(p):
            return p
    return "sau"


def build(platform, account, pack, video_file, project, headed):
    prefix, sub = PLATFORMS[platform]
    content = pack.get("content", {})
    if platform in CAPTION_PLATFORMS:
        title = content.get(prefix + "Caption", "")
    else:
        title = content.get(prefix + "Title", "")
    desc = content.get(prefix + "Desc", "") or content.get(prefix + "Caption", "")
    tags = content.get(prefix + "Tags", []) or []

    missing = []
    if not title:
        missing.append(prefix + ("Caption" if platform in CAPTION_PLATFORMS else "Title"))
    if not video_file:
        missing.append("videoFile / --file")
    if missing:
        raise SystemExit("[错误] 内容包缺少字段: " + ", ".join(missing))

    cmd = [find_sau(project)] + sub + ["--account", account, "--file", video_file, "--title", title]
    if desc:
        cmd += ["--desc", desc]
    if tags:
        cmd += ["--tags", ",".join(tags)]
    if platform == "bilibili" and content.get("bilibiliTid") is not None:
        cmd += ["--tid", str(content["bilibiliTid"])]
    if platform == "zhihu":
        if content.get("zhihuCategory"):
            cmd += ["--category", str(content["zhihuCategory"])]
        if content.get("zhihuVideoMark"):
            cmd += ["--video-mark", str(content["zhihuVideoMark"])]
    if platform == "youtube":
        cmd += ["--visibility", str(content.get("youtubeVisibility", "public"))]
    if headed:
        cmd.append("--headed")
    return cmd


def to_shell(cmd):
    return " ".join(shlex.quote(x) for x in cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    ap.add_argument("--account", required=True)
    ap.add_argument("--file", default=None, help="默认取内容包 videoFile")
    ap.add_argument("--project", default=r"D:\Mydata\github\social-auto-upload")
    ap.add_argument("--no-headed", action="store_true", help="不加 --headed（默认加）")
    ap.add_argument("--execute", action="store_true", help="真正执行；默认只打印命令")
    args = ap.parse_args()

    with open(args.pack, "r", encoding="utf-8") as f:
        pack = json.load(f)

    video = args.file or pack.get("videoFile")
    if video and not os.path.isabs(video):
        video = os.path.join(os.path.dirname(os.path.abspath(args.pack)), video)

    cmd = build(args.platform, args.account, pack, video, args.project, not args.no_headed)

    if video and not os.path.isfile(video):
        print(f"[警告] 视频文件不存在: {video}")
        print("       用 --file 指定实际路径，或修正内容包的 videoFile。")
        if args.execute:
            print("已取消执行。")
            return 2

    print("命令:")
    print(to_shell(cmd))
    print()

    if not args.execute:
        print("DRY-RUN：未执行。确认无误后加 --execute。")
        return 0

    print("执行中...")
    proc = subprocess.run(cmd, cwd=args.project, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(proc.stdout)
    if proc.stderr:
        print("[stderr]")
        print(proc.stderr)
    print("exit=", proc.returncode)
    return proc.returncode


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
