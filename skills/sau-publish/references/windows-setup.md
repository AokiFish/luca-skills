# Windows 安装与踩坑（social-auto-upload）

## 一、版本硬约束

- `pyproject.toml` 要求 `requires-python = ">=3.10,<3.13"`，Python 3.13 会直接不满足。
- 本机 Python 版本超标时，不要硬用系统解释器，用 uv 建合规环境：

```powershell
cd D:\Mydata\github\social-auto-upload
uv sync --python 3.12
```

## 二、必做初始化

```powershell
Copy-Item conf.example.py conf.py
```

缺 `conf.py` 时报错会指向 `sau_commands\arguments.py` 的 `from conf import BASE_DIR`，容易误判为依赖缺失。

## 三、浏览器下载（最容易卡住）

`patchright` 的版本决定它要下载哪个 Chromium build。官方 CDN（cdn.playwright.dev）在本网络环境会 ECONNRESET；npmmirror 镜像常缺最新 build（404 NoSuchKey）。

**正确顺序**：

1. 先用 HEAD 探测镜像上真实存在的 build：

```powershell
(Invoke-WebRequest -Method Head -Uri "https://cdn.npmmirror.com/binaries/playwright/builds/chromium/1148/chromium-win64.zip" -TimeoutSec 20).StatusCode
```

2. 把 patchright 降到与该 build 对应的版本（1148 对应 `patchright==1.49.1`）：

```powershell
uv pip install "patchright==1.49.1"
```

3. 用镜像安装：

```powershell
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://cdn.npmmirror.com/binaries/playwright"
.\.venv\Scripts\patchright.exe install chromium
```

4. 若只有 `chromium-headless-shell` 报 404、主 Chromium 已下载成功，忽略退出码即可——统一用 `--headed` 运行，不需要 headless shell。

## 四、常用路径

| 项 | 位置 |
|---|---|
| CLI | 项目根 `.venv\Scripts\sau.exe` |
| 浏览器 | `%LOCALAPPDATA%\ms-playwright\chromium-<build>` |
| 账号 cookie | 项目根 `cookies\<platform>_<account>.json` |
| 日志 | 项目根 `logs\<platform>.log` |
| 验证码文件 | 项目根 `verify_code.txt` |

## 五、踩坑速查表

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: No module named 'conf'` | 缺 conf.py | 复制 conf.example.py |
| `No module named pip` | uv 建的 venv 默认无 pip | 用 `uv pip` 而不是 `python -m pip` |
| `patchright install` 退出码 1 | 通常是 headless shell 404，主浏览器已好 | 换 `--headed` |
| `ECONNRESET` / `142.250.x.x` | 官方 CDN 不可达 | 用国内镜像 + 版本对齐 |
| `404 NoSuchKey` | 镜像没有该 build | 降 patchright 版本对齐 |
| 登录/发布启动失败 | 用了 `--headless` | 改 `--headed` |
| 发布报“成功”但后台没作品 | 误判或验证码未过 | 按 result-verification 核验 |
