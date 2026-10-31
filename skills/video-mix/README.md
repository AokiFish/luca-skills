# video-mix（多段视频拼接 + 自动配乐）

把一个目录里的 N 段短视频按文件名顺序拼成一个完整长视频，抹掉原音轨，按各段画面情绪重新生成与动作节奏匹配的背景音乐。

## 特性

- 自动校验分辨率/帧率一致，不一致直接报错，不硬拼
- 无损拼接（`-c:v copy`），视频流不二次编码
- 输出 H.264 + AAC，`-movflags +faststart`，可直接上传 X/Twitter、抖音、微信
- 中间产物统一进 `<目录>/_work/`，不污染用户素材目录
- 跨 Agent：不绑定 Doubao / Claude / Codex 任何一家的私有 API，音频生成走宿主原生能力

## 安装

依赖命令行工具（非 Python 包）：

- `ffmpeg` + `ffprobe`：需在 PATH 里
- Python 3.8+

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# 下载 https://ffmpeg.org/download.html，解压后把 bin/ 加到 PATH
```

## 用法

### 第一步：拼接（拿总时长）

```bash
python scripts/concat.py --input-dir "/path/to/clips"
```

输出 JSON，含 `total_duration`、`files`、`merged_silent` 路径。

### 第二步：让 Agent 按画面情绪生成配乐

参考 `SKILL.md` 的流程：抽帧看情绪 → 写分段式 prompt → 调用宿主音频生成能力 → 下载 wav 到 `<目录>/_work/music.wav`。

### 第三步：混合输出

```bash
python scripts/concat.py \
    --input-dir "/path/to/clips" \
    --music "/path/to/clips/_work/music.wav"
```

输出 JSON，含 `output_path`。

## 输出文件

- 最终视频：`<目录>/<目录名>_mixed.mp4`
- 中间产物：`<目录>/_work/`（merged_silent.mp4、concat.txt、抽帧、music.wav），可随时删除

## 不做什么

- 不硬拼分辨率/帧率不一致的片段
- 不做逐帧动作卡点对齐（需额外 librosa 重拍分析）
- 不保留原视频音轨
- 不做字幕、转场、变速
