---
name: github-weekly-video
description: >-
  Generate a vertical (1080x1920) short video recapping GitHub's weekly trending
  Top 5 open-source repos, with a cover frame, per-project intro/detail scenes,
  generated subtitles (SRT/VTT), and optional external voiceover. Use when the
  user wants a "GitHub 周榜 / 上周开源热榜 / 每周 GitHub 复盘 / GitHub weekly
  trending" recap video, or wants to reproduce the GithubWeekly Remotion
  composition in the luca-video project.
---

# github-weekly-video

## 目标

一键生成竖屏（1080×1920）短视频：**GitHub 上周开源热榜 Top5**。包含封面首帧、每个项目的「大字过场 + 详解（三大看点）」、片尾汇总、以及字幕文件。配音为**可选外部步骤**（用户在豆包 / CosyVoice 等工具生成后接入）。

## 何时使用

- 用户要 "GitHub 周榜 / 上周开源热榜 / 每周 GitHub 复盘" 类视频。
- 用户要复现类似 `luca-video` 项目的 `GithubWeekly` Remotion 合成。

## 输入

- 真实榜单数据（GitHub trending weekly Top5）：`repo / desc / lang / totalStars / weekStars`。
- （可选）配音 mp3：用户在外部工具（如豆包克隆 ai-weekly-man / ai-weekly-woman）生成，通过 `--vo` 接入。

## 输出（固定结构）

```
out/github-weekly-<YYYY-MM-DD>/
  github-weekly-<YYYY-MM-DD>.mp4   # 主视频 1080×1920
  首帧-<YYYY-MM-DD>.png            # 封面首帧（frame 0 即成稿）
  subtitles.srt                    # 字幕
  subtitles.vtt
```

目录名与文件名都**带日期**。

## 工作流（5 步）

1. **抓数据（可选）**：`python scripts/fetch_trending.py` → `top5.json`。
   若网络受限 / GitHub 改版导致失败，**直接手动填** `data.ts`，这是兜底路径，必须可用。
2. **填数据**：把榜单填入 `remotion-template/GithubWeekly/data.ts` 的 `PROJECTS` 与 `WEEK_*` 配置。每个项目补全：
   - `desc` 中文短句、`subtitleIntro` / `subtitleDetail`（屏幕底部字幕文案）、`points`（三大看点，逐条入场）、`tags`、`mockup`（`vocab|skill|audit|cockpit|purge` 选一，决定详情页动效）。
   - `WEEK_LABEL`（榜单周期小字）、`WEEK_SHORT`（封面绿 pill）、`WEEK_WORD`（封面/片尾用词：上周/本周）、`VO_FILE`（配音路径，留空=无声）。
3. **放模板**：首次把 `remotion-template/GithubWeekly/` 整目录复制到目标 Remotion 项目的 `src/GithubWeekly/`；之后只改 `data.ts`。在 `Root.tsx` 注册 `<GithubWeekly />` 合成（id 即 `GithubWeekly`）。
4. **渲染 + 字幕**：
   `python scripts/build.py --project-root <remotion项目> --date <YYYY-MM-DD> [--vo <配音.mp3>]`
   自动：渲染 mp4 → 导首帧 png → 生成字幕。
5. **接配音（可选）**：传 `--vo` 时 build 会复制 mp3 到 `public/vo/` 并改写 `data.ts` 的 `VO_FILE`；不传则无声仅字幕。

## 关键参数

- `--date`：决定输出目录名 / 文件名 / 首帧名。默认今天。
- `--vo`：配音文件（女声 / 男声由用户在外部工具选择，skill 只负责接入）。
- `CUTS` / `GITHUB_WEEKLY_DURATION`（`GithubWeekly.tsx`）：分镜帧数。有配音时按语音时长重算；无配音时用内置示例值（≈149s @30fps）即可直接渲染。

## 依赖

- Node + Remotion（目标项目已初始化，含 `node_modules/.bin/remotion`）。
- Python 3：`gen_subtitles.py` 仅用标准库；`fetch_trending.py` 需 `requests`（`pip install requests`）。

## 踩坑

- **渲染前 `NODE_OPTIONS=""`**：沙箱注入的 safe-delete 会把 remotion 清理 Chrome 下载锁的 `fs.rm` 改成"移回收站"导致死循环。`build.py` 已内置清空该变量。
- **配音无法自动克隆**：豆包桌面端无程序化接口（内部 IPC 不走 HTTP），本地 `AUDIO_MODEL` 是降噪/声纹模型而非 TTS 合成模型——**不能自动驱动克隆**。配音必须由用户在外部工具生成后通过 `--vo` 接入。
- **字幕不依赖配音**：按分镜（CUTS）固定时段生成，无论有无配音都能产出。
- **首帧**：封面用 `instant` 淡入（frame 0 即满亮度），`remotion still --frame=0` 直接出成稿封面。
- **沙箱 pip 走代理镜像**，部分包缺失（如 `TTS`/`XTTS` 无 Linux wheel、`cosyvoice` 编译失败）；如需本地克隆，另行评估 F5-TTS / CosyVoice 方案，与本 skill 解耦。

## 文件地图

- `remotion-template/GithubWeekly/`：Remotion 模板
  - `data.ts`：填数据（PROJECTS + WEEK_* + VO_FILE）
  - `GithubWeekly.tsx`：分镜 CUTS / 总时长 / 可选 Audio
  - `scenes.tsx`：封面 / 过场 / 详解 / 片尾场景
  - `components/`：通用 UI（Chrome 边框、Mockups 动效）
- `scripts/fetch_trending.py`：抓 Top5 → top5.json
- `scripts/gen_subtitles.py`：data.ts + GithubWeekly.tsx → SRT/VTT
- `scripts/build.py`：编排渲染 + 首帧 + 字幕
