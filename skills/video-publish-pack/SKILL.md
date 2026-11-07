---
name: video-publish-pack
description: 一次制作、多平台适配的视频发布物料生成器。为同一条视频，按抖音、小红书、B站、快手、视频号、百家号、微博、虎扑、知乎、YouTube、TikTok、Instagram、Facebook 等各平台的标题字数、描述结构、标签数量规则，生成各自适配的文案内容包（douyinTitle、xhsTitle、bilibiliTitle、youtubeTitle 等平台专用字段），并输出中英双语 SRT/VTT 字幕、按平台自动选字幕语言。作为 social-auto-upload 等发布工具的文案适配层：它只负责决定"每个平台发什么文案和哪套字幕"，发布执行交给 CLI/发布工具。当用户要把一条视频分发到多个平台、或要求按各平台规则生成标题/描述/标签/字幕时使用。
---

# 多平台视频发布物料生成器（适配层）

**定位**：social-auto-upload 负责"把内容发出去"，本 skill 负责"每个平台发什么文案、配哪套字幕"。同一份内容按平台规则重新适配，输出一份内容包（content-pack.json），发布工具直接消费。

## 核心概念：一次制作，多平台适配

```
基础内容（一条视频的真实信息：人物、故事、看点、语气、语言）
        │
        ▼
按平台规则逐平台改写（标题长度 / 描述结构 / 标签文化 / 语气 / 字幕语言）
        │
        ▼
content-pack.json（xhsTitle、douyinTitle、bilibiliTitle、youtubeTitle … + subtitleByPlatform）
        │
        ▼
social-auto-upload CLI 逐平台发布（title + desc + tags + 对应语言字幕）
```

不生产"一份文案全平台通用"，而是"一份内容，多份平台文案、双语字幕按平台取用"。

## 输入收集

| 字段 | 说明 | 缺失默认 |
|---|---|---|
| 视频来源 | 文件 / 链接 / 分镜脚本 / 剧情描述 | 必须提供或可提取 |
| 视频内容 | 发生了什么：剧情、看点、翻车点、名场面、金句 | 必须 |
| 出镜人设 | 角色名、形象、性格、说话风格 | 从材料提取 |
| 时长 / 比例 | 决定 Shorts 竖屏或横屏长视频，影响文案节奏 | 询问或按 16:9 处理 |
| 目标平台 | 用户点名的平台清单 | 默认全部 16 个平台；用户点名则只做点名平台 |
| 语言 | 中文平台用中文，海外平台用英文（或跟随用户指定） | 按平台自动切换 |
| 画面文字 | 是否已内嵌字幕 | 内嵌则不出外挂字幕 |
| 字幕语言 | 中文 / 英文 / 中英双语 | 默认中英双语，各平台按语言选用 |

## 内容包 Schema（交付核心）

交付 `content-pack.json`，字段按 `<platform>Title / <platform>Desc / <platform>Tags` 命名：

```json
{
  "schema": "video-publish-pack/v1",
  "videoFile": "videos/demo.mp4",
  "durationSec": 15,
  "aspectRatio": "16:9",
  "base": {
    "subject": "Mimi",
    "story": "小猫首播自我介绍连续翻车",
    "keyPoints": ["首支视频社死", "一本正经反差", "水打湿铃铛蝴蝶结"],
    "tone": "cute-comedy",
    "language": "zh"
  },
  "content": {
    "douyinTitle": "...",
    "douyinDesc": "...",
    "douyinTags": ["..."],
    "xhsTitle": "...",
    "xhsDesc": "...",
    "xhsTags": ["..."],
    "bilibiliTitle": "...",
    "bilibiliDesc": "...",
    "bilibiliTags": ["..."],
    "bilibiliTid": 249,
    "kuaishouTitle": "...", "kuaishouDesc": "...", "kuaishouTags": ["..."],
    "tencentTitle": "...", "tencentDesc": "...", "tencentTags": ["..."],
    "baijiahaoTitle": "...", "baijiahaoDesc": "...", "baijiahaoTags": ["..."],
    "weiboTitle": "...", "weiboDesc": "...", "weiboTags": ["..."],
    "hupuTitle": "...", "hupuDesc": "...", "hupuTags": ["..."],
    "zhihuTitle": "...", "zhihuDesc": "...", "zhihuTags": ["..."],
    "youtubeTitle": "...", "youtubeDesc": "...", "youtubeTags": ["..."],
    "tiktokCaption": "...", "tiktokTags": ["..."],
    "instagramCaption": "...", "instagramTags": ["..."],
    "facebookTitle": "...", "facebookDesc": "...",
    "alipayTitle": "...", "alipayDesc": "...", "alipayTags": ["..."],
    "dayuTitle": "...", "dayuDesc": "...", "dayuTags": ["..."],
    "xueqiuTitle": "..."
  },
  "subtitles": {
    "zh": { "srt": "subtitles.zh.srt", "vtt": "subtitles.zh.vtt" },
    "en": { "srt": "subtitles.en.srt", "vtt": "subtitles.en.vtt" }
  },
  "subtitleByPlatform": {
    "douyin": "zh", "xhs": "zh", "bilibili": "zh", "kuaishou": "zh", "tencent": "zh",
    "baijiahao": "zh", "weibo": "zh", "hupu": "zh", "zhihu": "zh",
    "alipay": "zh", "dayu": "zh", "xueqiu": "zh",
    "youtube": "en", "tiktok": "en", "instagram": "en", "facebook": "en"
  }
}
```

规则：
- 只填用户点名平台的字段；未点名平台不生成，保持内容包精简。
- 每个平台字段必须满足 `references/platform-rules.md` 的硬限制。
- `base` 只写视频真实信息，不写用于发布的文案（防止各平台文案被"基准版"污染）。
- 小红书、快手、抖音的图片笔记场景，`<platform>Desc` 可作为 note 正文使用。
- 字幕默认中英两套（`subtitles.zh` / `subtitles.en`），时间轴逐条一致、仅文本不同；`subtitleByPlatform` 声明各平台用哪套（国内 zh、海外 en）。用户只要单一语言时，只保留对应语言并省略 `subtitleByPlatform`。

## 工作流（五步）

1. **提炼 base**：通读输入，写 `base`（人物、故事、关键看点、语气、语言），找出 1-3 个跨平台通用的记忆点。
2. **定平台清单**：确认目标平台；默认全平台，用户点名则缩减。
3. **逐平台改写**：按 `references/platform-rules.md` 的长度限制 + `references/platform-playbooks.md` 的平台语气/标签文化，逐平台写标题、描述、标签。**先满足硬限制，再优化表达**。
4. **写内容包并校验**：输出 `content-pack.json`，运行 `python scripts/validate_pack.py content-pack.json` 校验字数/标签数/字幕语言映射；不合规字段重写，不硬截断。
5. **交付（必须逐项打勾，少一个都不算完）**：

   交付前必须用以下清单逐项核对，**每一个文件都必须真实存在于磁盘上**，不允许只在 content-pack.json 里写路径而不生成文件：

   - [ ] `content-pack.json` — 运行 `python scripts/validate_pack.py`，结果 **0 error**
   - [ ] `titles-by-platform.md` — 人类可读的全平台文案对照表
   - [ ] **视频画面已烧录字幕**（不是外挂 SRT 文件，是 ffmpeg 烧到 mp4 画面里的中文字幕）
   - [ ] `subtitles.zh.srt` — 中文字幕 SRT（时间轴对齐旁白）
   - [ ] `subtitles.zh.vtt` — 中文字幕 VTT（YouTube 用）
   - [ ] `subtitles.en.srt` — 英文字幕 SRT（与中文字幕同时间轴）
   - [ ] `subtitles.en.vtt` — 英文字幕 VTT（与中文字幕同时间轴）

   **字幕不是可选项**：只要视频有旁白，就必须：① 用 ffmpeg 把中文字幕烧录到视频画面里（`ffmpeg -i input.mp4 -vf "subtitles=subtitles.zh.srt:force_style='FontName=Microsoft YaHei,FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=40'" -c:a copy output.mp4`）；② 同时生成中英双语外挂 SRT/VTT 文件。两套字幕时间轴逐条一致，只换文本。

## 与 social-auto-upload 字段映射

| 内容包字段 | CLI 参数 |
|---|---|
| `douyinTitle/Desc/Tags` | `sau douyin upload-video --title --desc --tags` |
| `xhsTitle/Desc/Tags` | `sau xiaohongshu upload-video --title --desc --tags` |
| `bilibiliTitle/Desc/Tags/Tid` | `sau bilibili upload-video --title --desc --tags --tid` |
| `kuaishouTitle/Desc/Tags` | `sau kuaishou upload-video --title --desc --tags` |
| `tencentTitle/Desc/Tags` | `sau tencent upload-video --title --desc --tags` |
| `baijiahaoTitle/Desc/Tags` | `sau baijiahao upload-video --title --desc --tags` |
| `weiboTitle/Desc/Tags` | `sau weibo upload-video --title --desc --tags` |
| `hupuTitle/Desc/Tags` | `sau hupu upload-video --title --desc --tags` |
| `zhihuTitle/Desc/Tags` | `sau zhihu upload-video --title --desc --category` |
| `youtubeTitle/Desc/Tags` | `sau youtube upload-video --title --desc --tags` |
| `alipayTitle/Desc/Tags` | `sau alipay upload-video --title --desc --tags` |
| `dayuTitle/Desc/Tags` | `sau dayu upload-video --title --desc --tags` |
| `xueqiuTitle` | `sau xueqiu upload-article --title --content-file` |
| TikTok / Instagram / Facebook | 浏览器版，无 `sau` CLI（TikTok 无 CLI；Facebook/Instagram 有 CLI，见项目 README） |

标签数组传给 `--tags` 时用英文逗号拼接：`tag1,tag2,tag3`。

## 核心约束

1. **硬限制优先**：标题超字数必须重写，不能截断、不能加省略号凑数。
2. **平台语气差异**：小红书种草口语、B站信息密度、抖音强钩子、知乎专业、微博时效、虎扑玩梗、YouTube 搜索导向——同一视频不能照搬同一句。
3. **标签文化**：抖音/快手/视频号话题少而准；小红书话题可多（≤10）；YouTube 标签重搜索词；Instagram hashtag 收紧至 5 个内。
4. **语言分层**：中文平台中文、海外平台英文；不要中英混排除非用户要求。
5. **不编造**：所有文案只基于视频真实内容；不承诺视频里没有的信息。
6. **待核实平台**（支付宝生活号等）：交付时注明"以发布页实际限制为准"。
7. **字幕双语分层**：中文平台（抖音/小红书/B站/快手/视频号/百家号/微博/虎扑/知乎/支付宝/大鱼号/雪球）用 `zh` 字幕；海外平台（YouTube/TikTok/Instagram/Facebook）用 `en` 字幕。两套时间轴逐条对齐，只换文本，不得各自漂移。
8. **文案与视频同步**：视频叙事/旁白改了之后，content-pack.json 里的标题、描述、标签必须同步更新，不能视频是新故事、文案还是旧版本。生成文案前先重读视频旁白或分镜脚本。
9. **GitHub 标签必带**：做 GitHub 开源项目相关视频时，每个平台的标签列表里必须包含 `GitHub`，描述里必须提到仓库地址。
10. **封面规格适配**：按平台用户场景选择封面比例，不是所有平台都用同一张封面：
    - **YouTube 教学视频（横版长视频）**：16:9 横版封面（1280×720）
    - **抖音、快手（短视频竖屏）**：9:16 竖版封面（1080×1920）
    - **小红书**：3:4 竖版封面（1080×1440）
    - **视频号**：支持横版+竖版双封面（4:3 横版 + 3:4 竖版）
    - **B站**：16:9 横版封面（1146×717）
    - **微博**：16:9 横版封面
    - **百家号**：16:9 横版封面（必填）
    - **虎扑**：支持自定义封面（可选）
    - **TikTok / Instagram / Facebook**：9:16 竖版封面（短视频场景）
    - **知乎**：16:9 横版封面
    - 内容包 `covers` 字段声明各平台封面文件路径，发布时由 sau CLI 按 `--thumbnail` 参数传入。

## 资源导航

| 资源 | 何时读取 |
|---|---|
| `references/platform-rules.md` | 生成任何平台文案前必读（长度/标签硬限制） |
| `references/platform-playbooks.md` | 逐平台改写时读对应平台的语气与标签策略 |
| `references/title-strategies.md` | 需要标题多版本备选时读 |
| `references/subtitle-spec.md` | 生成 SRT/VTT 字幕、处理双语与平台选用时读 |
| `scripts/validate_pack.py` | 内容包生成后校验 |
| `examples/mimi-debut/` | 需要"一条视频 → 多平台内容包 + 中英字幕"成品参考时读 |
