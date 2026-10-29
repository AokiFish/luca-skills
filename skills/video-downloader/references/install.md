# 安装 yt-dlp 与 ffmpeg

## yt-dlp
任选其一：

```bash
# Python（推荐，跨平台）
python -m pip install -U yt-dlp

# 或直接下载独立可执行文件
# Windows: https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
# macOS/Linux: 下载 yt-dlp 后 chmod +x 并放到 PATH
```

验证：
```bash
yt-dlp --version
```

## ffmpeg（合并音视频必需）
yt-dlp 下载到分离的音视频流后，需要 ffmpeg 合并成单个 mp4。没有 ffmpeg 时，脚本会警告，且 `--merge-output-format mp4` 会失败。

- Windows：用 winget / scoop / chocolatey 安装，或下载 ffmpeg 静态构建并加入 PATH。
  ```bash
  winget install ffmpeg
  ```
- macOS：`brew install ffmpeg`
- Linux (Debian/Ubuntu)：`sudo apt install ffmpeg`

验证：
```bash
ffmpeg -version
```

## 验证整个链路（不下载大文件）
只看某个链接有哪些格式、能否解析，不真正下载：
```bash
python skills/video-downloader/scripts/download.py "<URL>" --list
```
能列出格式即说明提取器可用；列不出通常是该平台不支持或需要 cookie。
