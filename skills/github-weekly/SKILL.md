---
name: github-weekly
description: >-
  用 Remotion 一键生成 GitHub 周榜 Top5 竖屏解说短视频（1080x1920, 30fps），并自动接配音（先克隆声音再配音）、出封面首帧、生成字幕与标题文案。当用户说"做本周GitHub热榜视频""做一期github weekly""github周榜解说""GitHub热门项目视频"，或以 /M /W 指定配音性别时触发。M=男声、W=女声（默认女声），随时可换。输入框以 /github-weekly 调用。
---

# github-weekly

竖屏（1080×1920, 30fps）短视频：**GitHub 本周/上周开源热榜 Top5**。包含封面首帧、每个项目的「大字过场 + 详解（三大看点）」、片尾汇总、字幕（SRT/VTT），以及**自动配音**（默认女声，`/M` 或"男声"换男声，随时可换）。

## 何时使用

- 用户要 "GitHub 周榜 / 本周开源热榜 / 每周 GitHub 复盘" 类短视频。
- 用户要复现 `luca-video` 项目的 `GithubWeekly` Remotion 合成，或按 M/W 模式出片。

## 日期口径（固定）

- **每周一制作**，总结**上一周周一至周日**的开源热榜（制作日所在周的前一周）。
- `WEEK_LABEL` / `WEEK_SHORT` 按上一周区间填写：例如制作日 `2026-11-02`（周一）→ 上一周为 `10.26–11.01`，`WEEK_LABEL="10.26–11.01 周榜"`，`WEEK_SHORT="11月第1周"`。
- `WEEK_WORD`：上一周用"上周"。
- 输出目录 `out/github-weekly-<YYYY-MM-DD>/` 的日期用**制作日**（周一）。

## 声音选择

| 指定方式 | 声音 | 参考声源 |
| --- | --- | --- |
| （默认） | 女声 | `{VOICE_DIR}/ai-weekly-woman.mp3` |
| `/M` 或"男声" | 男声 | `{VOICE_DIR}/ai-weekly-man.mp3` |

- `VOICE_DIR` 默认 `D:\self-media\projects\luca-video\Voiceover`，可改。
- **先克隆再配音**，禁止 TTS 播音腔。详见 `references/voiceover.md`。

## 输入

- 真实榜单数据（GitHub trending weekly Top5）：`repo / desc / lang / totalStars / weekStars`。
- （自动）参考声源：`{VOICE_DIR}/ai-weekly-{woman|man}.mp3`。

## 输出（固定结构）

```
out/github-weekly-<YYYY-MM-DD>/
  github-weekly-<YYYY-MM-DD>.mp4   # 主视频 1080×1920
  首帧-<YYYY-MM-DD>.png            # 封面首帧（frame 0 即成稿）
  subtitles.srt / subtitles.vtt    # 字幕
  github-weekly-<YYYY-MM-DD>.md    # 标题 + 说明文案（发短视频用）
```

## 工作流（一键）

1. **抓数据**：`python scripts/fetch_trending.py` → `top5.json`。网络受限则**直接手动填** `data.ts`（兜底路径，必须可用）。
2. **填数据**：把 Top5 填入 `remotion-template/GithubWeekly/data.ts` 的 `PROJECTS` 与 `WEEK_*`。每个项目补全：`desc`（中文短句）、`subtitleIntro` / `subtitleDetail`（底部字幕）、`points`（三大看点）、`tags`、`mockup`（`vocab|skill|audit|cockpit|purge` 选一）。填 `WEEK_LABEL` / `WEEK_SHORT` / `WEEK_WORD`。
3. **放模板**：首次把 `remotion-template/GithubWeekly/` 整目录复制到目标项目 `src/GithubWeekly/`，并在 `Root.tsx` 注册 `<GithubWeekly />`（id 即 `GithubWeekly`）；之后只改 `data.ts`。
4. **写解说词**：按 `references/voiceover.md` 的模板写 `narration.txt`（12 行，每行一个场景台词）。
5. **克隆并生成配音**：上传参考声源 → `audio_to_audio_plus` 生成完整旁白 → 下载 `public/vo/vo-full.mp3`。（细节见 `references/voiceover.md`）
6. **对齐 + 渲染**：
   ```powershell
   python scripts/build.py --project-root . --date <YYYY-MM-DD> --vo public/vo/vo-full.mp3 --narration narration.txt
   ```
   自动：接入配音 → `gen_cuts.py` 对齐分镜 → 渲染 mp4 → 首帧 png → 字幕。不传 `--vo` 则无声仅字幕。
7. **标题 + 说明**：`python scripts/gen_copy.py --data src/GithubWeekly/data.ts --outdir out/github-weekly-<date> --date <date>` 自动从 data.ts 生成 `github-weekly-<date>.md`（标题 + 1～5 项目说明 + 合计星数 + 英文推广段）。脚本产物是草稿，按 `references/output-copy.md` 的模板润色标题亮点与说明措辞。
8. **交付**：用 `<RichMediaCard>` 交付 mp4。所有文件已在 `out/github-weekly-<date>/` 子目录，不散落。

## 关键脚本

- `scripts/fetch_trending.py` — 抓 Top5 → `top5.json`
- `scripts/gen_cuts.py` — silencedetect 停顿 + 字数比例 → 重写 CUTS/DURATION/VO_FILE
- `scripts/gen_subtitles.py` — data.ts + GithubWeekly.tsx → SRT/VTT（不依赖配音）
- `scripts/gen_copy.py` — data.ts → 标题+说明文案 md
- `scripts/build.py` — 编排：配音 → 对齐 → 渲染 → 首帧 → 字幕

## 依赖

- Node + Remotion（目标项目已初始化，含 `node_modules/.bin/remotion`）。
- Python 3：`gen_cuts.py` / `gen_subtitles.py` 仅标准库；`fetch_trending.py` 需 `requests`。
- ffmpeg（`gen_cuts.py` 做 silencedetect）。

## 踩坑

- **渲染前 `NODE_OPTIONS=""`**：沙箱注入的 safe-delete 会把 remotion 清理 Chrome 下载锁的 `fs.rm` 改成"移回收站"导致死循环。`build.py` 已内置清空该变量。
- **配音必须整段连续生成**：拆成多段会在句间插静音，听起来一卡一卡。若 `audio_to_audio_plus` 输出被截断（没说完），重新生成更长的版本。
- **字幕不依赖配音**：按分镜（CUTS）固定时段生成，无论有无配音都能产出。
- **首帧**：封面用 `instant` 淡入（frame 0 即满亮度），`remotion still --frame=0` 直接出成稿封面。

## 文件地图

- `remotion-template/GithubWeekly/`：Remotion 模板
  - `data.ts`：填数据（PROJECTS + WEEK_* + VO_FILE）
  - `GithubWeekly.tsx`：分镜 CUTS / 总时长 / Audio（VO_FILE 非空时播放）
  - `scenes.tsx`：封面 / 过场 / 详解 / 片尾场景
  - `components/`：通用 UI（Chrome 边框、Mockups 动效）
- `references/voiceover.md`：声音选择 + 克隆流程 + 解说词模板
- `references/output-copy.md`：标题与配套文案模板
- `scripts/`：抓数 / 对齐 / 字幕 / 编排
