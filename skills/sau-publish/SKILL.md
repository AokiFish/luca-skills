---
name: sau-publish
description: 用 social-auto-upload 的 `sau` CLI 把视频/图文真正发布到抖音、小红书、B站、快手、视频号、百家号、微博、虎扑、知乎、YouTube、支付宝、大鱼号等平台，覆盖 Windows 环境安装、扫码登录、cookie 维护、发布参数、短信验证码与发布结果核验。当用户说“发布到抖音/B站/小红书/视频号/YouTube”“全自动发布”“帮我把视频发出去”，或已有 content-pack.json 需要执行发布时使用。它是 video-publish-pack 的下游执行层：只负责发，不重新写文案。
---

# sau-publish：发布执行层

**定位**：`video-publish-pack` 决定“每个平台发什么文案”，本 skill 负责“把内容真正发出去”。不重新写文案，只消费内容包字段并调用 `sau` CLI。

## 前置判断（先花 30 秒查，不要直接下单）

| 检查项 | 怎么查 | 缺失怎么办 |
|---|---|---|
| 项目根 | `D:\Mydata\github\social-auto-upload`（以用户实际路径为准） | 让用户提供路径或按 `references/windows-setup.md` 安装 |
| 虚拟环境 | 项目根下 `.venv\Scripts\sau.exe` 是否存在 | 按 setup 文档重建 |
| `conf.py` | 项目根是否有 `conf.py` | `Copy-Item conf.example.py conf.py` |
| 浏览器 | `%LOCALAPPDATA%\ms-playwright\chromium-*` 是否有完整目录 | 按 setup 文档下载 |
| 账号 cookie | `cookies\<platform>_<account>.json` | 走登录流程 |

任一项缺失 → 读 `references/windows-setup.md` 按步骤补齐，不要临场猜命令。

## 完整工作流规范（视频→文案→发布）

从视频制作到发布，每个环节的强制规则。任一环节跳过即视为未完成。

### 环节一：视频渲染（Remotion）

| 规则 | 怎么做 | 为什么 |
|---|---|---|
| 复用设计系统 | import `../OmnigetTutorial/ui.tsx` 的 Stage/Window/SectionTitle/Pill/CaptionBar，不另建工程、不另写色块 | 保证和 OmnigetTutorial 风格一致 |
| 每场景 CaptionBar | 9 个场景每个都加 `<CaptionBar text={NARRATION.xxx} />`，text 传完整旁白 | 字幕在 Remotion 里渲染，不 ffmpeg 事后烧 |
| CUTS 用 ASR 实测 | 渲染前用 `mediakit-cli video asr-subtitles` 转写旁白音频，拿到逐句时间戳，按真实时间填 CUTS 帧位置（30fps） | 不预估，否则字幕和画面对不上 |
| 抽帧验证 | 渲染后抽 2-3 帧验证 CaptionBar 可见、时间轴对齐、没有双层叠加 | 不验证不说做完 |

### 环节二：文案与字幕（video-publish-pack）

| 规则 | 怎么做 |
|---|---|
| 内容包 | 生成 `content-pack.json`，运行 `validate_pack.py` 校验 0 error |
| 对照表 | 生成 `titles-by-platform.md` 人类可读对照表 |
| 双语字幕 | 生成 `subtitles.zh.srt/.vtt` 和 `subtitles.en.srt/.vtt`，时间轴按 ASR 实测结果 |
| GitHub 标签 | 每个平台标签列表必须带 `GitHub`，描述必须提仓库地址 |
| 文案与视频同步 | 视频叙事改了，文案必须同步更新 |

### 环节三：发布执行（本 skill）

| 规则 | 怎么做 |
|---|---|
| 检查登录态 | `sau <platform> check` 返回 valid 才继续 |
| 发布前复述 | 复述账号、视频路径、标题、描述、标签，用户确认才发 |
| 后台核验 | 发布后打开作品页确认状态"已发布"，日志里的"发布成功"不算证据 |
| 不盲目重传 | 状态不明时先核验后台，禁止重复发布 |

### 三条铁律（贯穿全流程）

1. **不预估时间轴**：CUTS、字幕时间戳必须 ASR 实测，不凭感觉算
2. **不瞎编内容**：字幕、文案、旁白必须和视频实际一致，不自己发挥
3. **不验证不交付**：抽帧验证视频、校验文案、确认后台状态，做完了才说做完

### 发布执行步骤（环节三展开）

1. **检查登录态**
   `sau <platform> check --account <name>`，返回 `valid` 才继续；`invalid` 走第 2 步。
2. **登录（仅首次或失效）**
   `sau <platform> login --account <name> --headed`
   - 浏览器会准备二维码，图片路径形如 `cookies\<platform>_<name>_login_qrcode_*.png`，**直接把图片展示给用户扫**，不要只给路径。
   - 抖音登录成功标志：页面跳到 `creator.douyin.com/creator-micro/home`，并生成 `cookies\douyin_<name>.json`。
3. **取字段**
   从 `content-pack.json` 按下面的映射取标题/描述/标签；标签数组用英文逗号拼接。
4. **发布**
   `sau <platform> upload-video --account <name> --file <mp4> --title "..." --desc "..." --tags "a,b,c" --headed`
5. **核验（必做）**
   日志里的“发布成功”不算证据。按 `references/result-verification.md` 打开后台作品页，确认状态“已发布”、标题正确、时长正确，再向用户报告。

## 内容包字段映射

| 内容包前缀 | CLI 子命令 | 封面参数 | 备注 |
|---|---|---|---|
| `douyin` | `sau douyin upload-video` | `--thumbnail-landscape` 横版 + `--thumbnail-portrait` 竖版 | 视频 `--desc`；图文 `upload-note --note` |
| `xhs` | `sau xiaohongshu upload-video` | `--thumbnail` 3:4 竖版 | 图片笔记用 `upload-note` |
| `bilibili` | `sau bilibili upload-video` | `--thumbnail` 16:9 横版 | 必带 `--tid`（内容包 `bilibiliTid`） |
| `kuaishou` | `sau kuaishou upload-video` | 无（系统自动截取） | — |
| `tencent` | `sau tencent upload-video` | `--thumbnail-landscape` 横版 + `--thumbnail-portrait` 竖版 | 支持 `--short-title`、合集 |
| `baijiahao` | `sau baijiahao upload-video` | `--thumbnail` 16:9 横版（**必填**） | 不提供封面会报错 |
| `weibo` | `sau weibo upload-video` | `--thumbnail` 16:9 横版（**必填**） | 标题 ≤30 字，封面 <5MB |
| `hupu` | `sau hupu upload-video` | `--thumbnail` 可选 | 标题 4–40 字 |
| `zhihu` | `sau zhihu upload-video` | `--thumbnail` 16:9 横版 | 需 `--category` 与 `--video-mark` |
| `youtube` | `sau youtube upload-video` | `--thumbnail` 16:9 横版 | 需 `--visibility` |
| `alipay` | `sau alipay upload-video` | `--thumbnail` 可选 | — |
| `dayu` | `sau dayu upload-video` | 无 | — |
| `tiktok` / `instagram` / `facebook` | 无统一 CLI | 浏览器版手动上传封面 | 如实告知用户需走浏览器版 |

字段命名：`<prefix>Title` / `<prefix>Desc` / `<prefix>Tags`；TikTok、Instagram 用 `<prefix>Caption`。
封面文件按 video-publish-pack 的 `covers` 字段路径传入。

## 硬约束

1. **一律加 `--headed`**：当前环境缺 chromium headless shell，`--headless` 会启动失败。
2. **发布前复述最终参数**（账号、视频路径、标题、描述、标签、立即/定时），用户明确说“直接发”可跳过复述。
3. **短信验证码**：抖音提交时可能弹验证码，CLI 会自动点“获取验证码”并反复重试。把收到的码写入项目根 `verify_code.txt` 即可继续；不要反复重跑命令。
4. **AI 内容声明**：视频含 AI 生成内容时，确认日志里有 `自主声明已选择「内容由AI生成」`；没有则到发布页手动勾选。
5. **超时不等于失败**：状态不明时先核验后台原作品，禁止盲目重传，避免重复作品。
6. **只发用户点名的平台**；发布是可撤销性低的外部动作，账号/内容/时间要对得上。

## 资源导航

| 资源 | 何时读 |
|---|---|
| `references/windows-setup.md` | 首次安装、CLI 起不来、浏览器下载失败、依赖版本冲突 |
| `references/login-and-cookie.md` | 登录、二维码展示、cookie 失效、多账号 |
| `references/douyin-publish.md` | 抖音发布参数、AI 声明、验证码、图文发布 |
| `references/result-verification.md` | 发布后核验、截图确认、判定标准 |
| `scripts/publish_from_pack.py` | 从 content-pack.json 直接生成或执行发布命令 |
| `scripts/verify_douyin_post.py` | 用 cookie 打开抖音作品管理页并截图核验 |
