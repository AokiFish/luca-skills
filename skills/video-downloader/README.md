# video-downloader（通用视频下载技能）

给一个主流平台的视频链接，下载为本地文件并返回路径。基于 **yt-dlp**，兼容任意 AI Agent 平台。

## 支持情况
| 平台 | 状态 |
|---|---|
| YouTube / X(Twitter) / Bilibili / TikTok / 微博 | ✅ 稳定可用 |
| 抖音 | ⚠️ 尽力而为（常需 cookie，易被限流） |
| 小红书 | ⚠️ 脆弱（仅部分视频笔记，图文笔记不支持） |
| Instagram / Facebook / Vimeo / Reddit | ✅ 走 yt-dlp 支持 |

不支持：DRM、付费墙、必须登录绕过、直播录制及无提取器的冷门平台。

## 安装
```bash
python -m pip install -U yt-dlp        # 必需
# ffmpeg 需单独安装并加入 PATH（合并音视频用）
```

## 用法
```bash
# 公开视频
python scripts/download.py "<URL>"

# 需要登录态的平台（抖音、小红书、B站番剧等）
python scripts/download.py "<URL>" --browser chrome
python scripts/download.py "<URL>" --cookies cookies.txt

# 只取音频 / 查看可选清晰度
python scripts/download.py "<URL>" --audio
python scripts/download.py "<URL>" --list
```

成功输出末尾一行 `DOWNLOADED: <绝对路径>`，可直接回传给用户。

## 失败处理
按提示做**一个**修复并最多重试一次；仍失败就报告确切限制与备选方案，不循环重试。

## 文件结构
- `SKILL.md` — 主入口与兼容性说明
- `scripts/download.py` — 跨平台封装脚本
- `references/platforms.md` — 各平台细节与 cookie 获取
- `references/install.md` — 依赖安装
- `evals/evals.json` — 行为回归断言
