---
name: video-downloader
description: "通用视频下载技能：给定任一主流平台的视频链接（YouTube、X/Twitter、Bilibili、抖音、小红书、TikTok、微博等），调用 yt-dlp 下载为本地文件并返回路径。兼容任意 AI Agent 平台。yt-dlp 失败时给出明确原因与下一步修复，而非盲目重试。不绕过 DRM、付费墙或登录限制。"
version: "0.01.0"
---

# Video Downloader（通用视频下载）

## Purpose
用户给一个链接，你就把它下载成可访问的本地视频文件。覆盖 YouTube、X/Twitter、Bilibili、抖音、小红书、TikTok、微博等主流平台，以及 Instagram / Facebook / Vimeo / Reddit 等 yt-dlp 已支持的站点。

核心是 **yt-dlp**——一个支持上千个站点的成熟下载器。本技能把它封装成「给 URL → 拿本地路径」的简单流程，并在失败时给出诚实的诊断与一次性修复建议。

## 兼容性（诚实说明，先读这个）
| 平台 | yt-dlp 支持 | 说明 |
|---|---|---|
| YouTube | ✅ 极佳 | 公开视频无需 cookie；年龄限制/私享需 cookie |
| X / Twitter | ✅ 良好 | 公开推文通常可用；部分媒体需 cookie |
| Bilibili | ✅ 极佳 | 公开可用；番剧/区域限制需 SESSDATA cookie |
| 抖音 Douyin | ⚠️ 尽力而为 | 有提取器，但常被限流或需 cookie；直播/区域内容可能失败 |
| 小红书 Xiaohongshu | ⚠️ 脆弱 | yt-dlp 有 XiaoHongShu 提取器，但仅支持部分视频笔记，常需 cookie；图文笔记不支持，经常失败 |
| TikTok | ✅ 良好 | 可用；部分地区需 cookie |
| 微博 Weibo | ✅ 良好 | 可用 |
| Instagram / Facebook / Vimeo / Reddit | ✅ 支持 | 走 yt-dlp |

**我做不到的（直说，不瞎试）：**
- 小红书图文/纯文字笔记——只支持部分视频笔记，且高概率失败，常需手动导出 cookie。
- DRM 保护内容、付费墙、必须登录才能看的内容——明确超出范围，不绕过。
- 实时直播——可录制但耗时且不稳定，按需求确认。
- yt-dlp 没有提取器的冷门/小众 App——不支持。

## Quick start（给 Agent 的指令）
首选调用封装脚本，跨平台、零额外依赖：

```bash
# 公开视频，直接下
python skills/video-downloader-skill/scripts/download.py "https://<平台链接>"

# 指定输出目录
python skills/video-downloader-skill/scripts/download.py "<URL>" --dir ./videos

# 需要登录/cookie 的平台（抖音、小红书、B站番剧等）
python skills/video-downloader-skill/scripts/download.py "<URL>" --browser chrome
# 或导出 cookies.txt 后用：
python skills/video-downloader-skill/scripts/download.py "<URL>" --cookies cookies.txt

# 只取音频
python skills/video-downloader-skill/scripts/download.py "<URL>" --audio

# 先看有哪些清晰度再决定（不下）
python skills/video-downloader-skill/scripts/download.py "<URL>" --list
```

成功后脚本输出一行 `DOWNLOADED: <绝对路径>`，把该路径回给用户。

## 不用脚本，直接调 yt-dlp 也行
不同 Agent 环境若不便跑 Python，可直接：

```bash
yt-dlp -f "bv*+ba/best" --merge-output-format mp4 -o "%(id)s.%(ext)s" "<URL>"
```

## 处理流程（失败时的回退阶梯，不要循环重试）
1. 先直接跑脚本，公开视频大多一次成功。
2. 失败 → 只读一次诊断输出，按提示做**一个**修复（更新 yt-dlp / 加 cookie），再重试**一次**。
3. 仍失败 → 向用户报告确切限制，并给一个简单备选：让用户提供直链、本地下载后上传、或换平台链接。**绝不反复盲试消耗 token。**
4. 若某平台 yt-dlp 确实无提取器，直接说明不支持，不要假装尝试。

## Cookie 怎么拿
- 浏览器导出：装「Get cookies.txt LOCALLY」类扩展，登录后导出 cookies.txt，用 `--cookies cookies.txt`。
- 或直接 `--browser chrome`（读取本机已登录浏览器的 cookie）。
- 平台细节见 `references/platforms.md`。

## 安装依赖
- yt-dlp：`python -m pip install -U yt-dlp`，或下载 `yt-dlp.exe`。
- ffmpeg：合并音视频必需，需置于 PATH。详见 `references/install.md`。
- 本技能 `requirements.txt` 仅列 yt-dlp 作为安装提示。

## 边界（行为红线）
- 不绕过任何站点的 DRM、付费墙、登录校验或访问限制。
- 下载后仅返回文件路径与基础元数据，不替用户解读视频内容。
- 遇到限流/失败，报原因 + 一次修复，不无限重试。
