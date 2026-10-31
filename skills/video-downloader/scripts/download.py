#!/usr/bin/env python3
"""
Universal video downloader wrapper around yt-dlp.

Agent-agnostic: any AI agent can call `python download.py "<URL>"` and get a
local file path back. No third-party Python dependencies are required beyond
yt-dlp itself (and ffmpeg for merging, which yt-dlp invokes automatically).

Design goals:
- One command for every platform yt-dlp supports (YouTube, X, Bilibili,
  Douyin, Xiaohongshu, TikTok, Weibo, Instagram, ...).
- Sensible defaults: best merged mp4, restricted filenames, single video.
- Clear, parseable output: a final `DOWNLOADED: <abs path>` line.
- Honest failures: prints the likely cause + the one fix to try next,
  instead of retrying blindly.
- Optional `--auto-proxy`: on Windows, read the system proxy from the registry
  and auto-route only overseas platforms through it, leaving CN platforms
  direct (bypasses proxy).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

DEFAULT_OUT = "./downloads"

# Domains that should NOT go through a proxy (CN platforms and local dev).
CN_DOMAIN_RE = re.compile(
    r"(?:^|\.)("
    r"bilibili\.com|b23\.tv|"
    r"douyin\.com|douyin\.com\.cn|"
    r"xiaohongshu\.com|xhslink\.com|"
    r"weibo\.com|weibo\.cn|"
    r"zhihu\.com|zhuanlan\.zhihu\.com|"
    r"baidu\.com|baidubce\.com|"
    r"qq\.com|tencent\.com|weixin\.qq.com|"
    r"alibaba\.com|taobao\.com|tmall\.com|alicdn\.com|"
    r"bilibili\.cn|"
    r"localhost|127\.0\.0\.1"
    r")$",
    re.IGNORECASE,
)


def find_executable(name, extra_dirs=None):
    """Locate an executable: PATH first, then common side-by-side / download dirs."""
    found = shutil.which(name)
    if found:
        return found
    candidates = list(extra_dirs or [])
    here = os.path.dirname(os.path.abspath(__file__))
    candidates += [
        os.path.join(here, name + ".exe"),
        os.path.join(here, name),
        os.path.join(os.path.expanduser("~"), "Downloads", "yt-dlp", name + ".exe"),
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def detect_windows_system_proxy():
    """Read Windows registry system proxy. Returns (proxy_str, bypass_list) or (None, None)."""
    if sys.platform != "win32":
        return None, None
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        )
        enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if not enable:
            return None, None
        server, _ = winreg.QueryValueEx(key, "ProxyServer")
        bypass, _ = winreg.QueryValueEx(key, "ProxyOverride") if True else ("",)
        winreg.CloseKey(key)
        if not server:
            return None, None
        # ProxyServer may be "http=127.0.0.1:10808;https=127.0.0.1:10809" or just "127.0.0.1:10808"
        m = re.search(r"https?=([^;]+)", server)
        if m:
            proxy = m.group(1)
        elif "=" in server:
            proxy = server.split("=")[-1]
        else:
            proxy = server
        if not proxy.startswith(("http://", "https://", "socks")):
            proxy = "http://" + proxy
        bypass_list = [b.strip() for b in bypass.split(";") if b.strip()] if bypass else []
        return proxy, bypass_list
    except Exception:
        return None, None


def is_cn_url(url):
    m = re.match(r"https?://([^/]+)", url, re.IGNORECASE)
    if not m:
        return False
    host = m.group(1).lower()
    return bool(CN_DOMAIN_RE.search(host))


def diagnose():
    sys.stderr.write(
        "\n=== DOWNLOAD FAILED ===\n"
        "Try fixes in order; do NOT loop. After one fix, retry once.\n"
        "1. Update yt-dlp:        python -m pip install -U yt-dlp\n"
        "2. 'login required' / 'Sign in to confirm': pass cookies ->\n"
        "     --cookies cookies.txt        (export via 'Get cookies.txt' extension)\n"
        "     or --browser chrome          (read cookies from local browser)\n"
        "3. 'rate-limited' / 'Too Many Requests': wait or use cookies.\n"
        "4. 'Unsupported URL': this platform/link has no yt-dlp extractor.\n"
        "5. 'Failed to extract': extractor broken; update yt-dlp and retry once.\n"
        "Platform-specific help: see references/platforms.md\n"
    )


def main():
    p = argparse.ArgumentParser(
        description="Download a video from any supported platform via yt-dlp."
    )
    p.add_argument("url", help="Video or page URL to download")
    p.add_argument("--dir", default=DEFAULT_OUT, help="Output directory (default: ./downloads)")
    p.add_argument("--cookies", help="Path to Netscape-format cookies.txt")
    p.add_argument(
        "--browser",
        help="Browser name for --cookies-from-browser (chrome/firefox/edge/brave/safari)",
    )
    p.add_argument(
        "--format",
        default="bv*+ba/best",
        help="yt-dlp format selector (default: bv*+ba/best)",
    )
    p.add_argument("--audio", action="store_true", help="Extract audio only as mp3")
    p.add_argument(
        "--list", action="store_true", help="List available formats and exit (no download)"
    )
    p.add_argument(
        "--simulate", action="store_true", help="Dry run: print metadata, do not download"
    )
    p.add_argument("--max-filesize", help="Abort if estimated size exceeds (e.g. 500M, 2G)")
    p.add_argument(
        "--no-merge", action="store_true", help="Keep separate video/audio (no mux)"
    )
    p.add_argument(
        "--playlist", action="store_true", help="Download whole playlist/channel, not just one item"
    )
    p.add_argument("--yt-dlp", help="Explicit path to yt-dlp executable")
    p.add_argument(
        "--auto-proxy",
        action="store_true",
        help="On Windows, auto-detect system proxy from registry and route only overseas platforms through it (CN platforms go direct).",
    )
    p.add_argument(
        "--proxy",
        help="Explicit proxy URL (e.g. http://127.0.0.1:10808). Overrides --auto-proxy.",
    )
    args = p.parse_args()

    yt = args.yt_dlp or find_executable("yt-dlp")
    if not yt:
        sys.stderr.write(
            "ERROR: yt-dlp not found.\n"
            "  Install:  python -m pip install -U yt-dlp\n"
            "  or download: https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe\n"
            "  ffmpeg is also required for merging: https://ffmpeg.org/download.html\n"
        )
        return 2

    if not (shutil.which("ffmpeg") or find_executable("ffmpeg")):
        sys.stderr.write(
            "WARNING: ffmpeg not found on PATH. Merging/muxing may fail.\n"
            "  Install ffmpeg and ensure it is on PATH.\n"
        )

    os.makedirs(args.dir, exist_ok=True)

    # --- Proxy routing -------------------------------------------------
    # If --proxy given, use it unconditionally.
    # Else if --auto-proxy on Windows, read registry system proxy and only
    # inject it when the URL is an overseas (non-CN) platform.
    proxy_to_use = args.proxy
    if not proxy_to_use and args.auto_proxy:
        sys_proxy, bypass = detect_windows_system_proxy()
        if sys_proxy:
            if is_cn_url(args.url):
                sys.stderr.write(
                    f"[auto-proxy] CN platform detected, bypassing system proxy ({sys_proxy})\n"
                )
                proxy_to_use = None
            else:
                sys.stderr.write(f"[auto-proxy] Overseas platform, using system proxy: {sys_proxy}\n")
                proxy_to_use = sys_proxy
        else:
            sys.stderr.write("[auto-proxy] No Windows system proxy detected, going direct.\n")

    if proxy_to_use:
        env = os.environ.copy()
        env["HTTPS_PROXY"] = proxy_to_use
        env["HTTP_PROXY"] = proxy_to_use
        env["https_proxy"] = proxy_to_use
        env["http_proxy"] = proxy_to_use
    else:
        env = os.environ.copy()

    cmd = [yt]
    if args.cookies:
        cmd += ["--cookies", args.cookies]
    if args.browser:
        cmd += ["--cookies-from-browser", args.browser]

    if not args.playlist:
        cmd += ["--no-playlist"]

    cmd += [
        "--restrict-filenames",
        "--no-warnings",
        "-P", args.dir,
        "-o", "%(id)s.%(ext)s",
    ]

    if args.list:
        return subprocess.call(cmd + ["--list-formats", args.url])

    if args.simulate:
        return subprocess.call(cmd + ["--simulate", "--dump-json", args.url])

    if args.audio:
        cmd += ["-x", "--audio-format", "mp3", "-f", "ba/best"]
    else:
        cmd += ["-f", args.format]
        if not args.no_merge:
            cmd += ["--merge-output-format", "mp4"]

    if args.max_filesize:
        cmd += ["--max-filesize", args.max_filesize]

    # Single machine-parseable line emitted after the file is written.
    cmd += [
        "--print",
        "after_move:FILE|%(filepath)s|TITLE|%(title)s|DUR|%(duration)s|EXT|%(ext)s",
    ]
    cmd.append(args.url)

    proc = subprocess.run(cmd, text=True, env=env)
    if proc.returncode != 0:
        diagnose()
        return proc.returncode

    path = title = dur = ext = None
    for line in (proc.stdout or "").splitlines():
        if line.startswith("after_move:"):
            parts = line[len("after_move:"):].split("|")
            d = {}
            for i in range(0, len(parts) - 1, 2):
                d[parts[i]] = parts[i + 1]
            path, title, dur, ext = d.get("FILE"), d.get("TITLE"), d.get("DUR"), d.get("EXT")
            break

    if not (path and os.path.isfile(path)):
        # Fallback: pick the most recently modified file in the output dir.
        try:
            files = [
                os.path.join(args.dir, f)
                for f in os.listdir(args.dir)
                if os.path.isfile(os.path.join(args.dir, f))
            ]
            if files:
                path = max(files, key=os.path.getmtime)
        except OSError:
            path = None

    if path and os.path.isfile(path):
        print("\n=== DOWNLOAD COMPLETE ===")
        print(f"PATH:    {path}")
        print(f"TITLE:   {title}")
        print(f"EXT:     {ext}")
        print(f"DURATION:{dur}s")
        print(f"DOWNLOADED: {path}")
        return 0

    print("\nDownload finished but final path not captured. Check:")
    print(f"  {os.path.abspath(args.dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
