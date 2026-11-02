#!/usr/bin/env python3
"""抓取 GitHub 本周 trending Top5，输出 top5.json 供 agent 填写 data.ts。

用法：
    python fetch_trending.py [--out top5.json]

说明：
- 走系统代理 / 直连均可，依赖 requests。
- 若抓取或解析失败（网络受限、GitHub 改版），脚本会报错退出，
  agent 应改为手动填写 data.ts 的 PROJECTS（这是兜底路径，必须可用）。
- 输出的 JSON 仅含原始字段（repo/desc/lang/totalStars/weekStars），
  中文解说文案（desc 的中文短句、subtitleIntro/Detail、points、tags、mockup）
  仍需 agent 基于真实信息补全。
"""
import argparse
import json
import re
import sys

try:
    import requests
except ImportError:
    requests = None

URL = "https://github.com/trending?since=weekly"


def fetch():
    if requests is None:
        sys.exit("缺少 requests，请先 `pip install requests` 或手动填写 data.ts")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    r = requests.get(URL, headers=headers, timeout=25)
    r.raise_for_status()
    return r.text


def parse(html):
    blocks = re.findall(r'<article class="Box-row">(.*?)</article>', html, re.S)
    repos = []
    for b in blocks[:5]:
        m = re.search(r'<h2[^>]*>.*?<a[^>]*href="/([^"]+)"', b, re.S)
        repo = m.group(1).strip() if m else None
        if not repo:
            continue
        d = re.search(r'<p[^>]*class="col-9[^"]*"[^>]*>(.*?)</p>', b, re.S)
        desc = re.sub(r"<[^>]+>", "", d.group(1)).strip() if d else ""
        desc = re.sub(r"\s+", " ", desc)
        l = re.search(r'itemprop="programmingLanguage">([^<]+)<', b, re.S)
        lang = l.group(1).strip() if l else ""
        s = re.search(r'href="/%s/stargazers"[^>]*>\s*([\d,]+)' % re.escape(repo), b, re.S)
        total = int(s.group(1).replace(",", "")) if s else 0
        w = re.search(r"([\d,]+)\s*stars (this week|today)", b, re.S)
        week = int(w.group(1).replace(",", "")) if w else 0
        # 语言颜色（GitHub 内联 style）
        c = re.search(r'style="[^"]*background-color:\s*([#\w]+)"', b)
        lang_color = c.group(1).strip() if c else "#888888"
        repos.append(
            {
                "repo": repo,
                "desc": desc,
                "lang": lang,
                "langColor": lang_color,
                "totalStars": total,
                "weekStars": week,
            }
        )
    return repos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="top5.json")
    a = ap.parse_args()
    html = fetch()
    repos = parse(html)
    if not repos:
        sys.exit("解析失败：未找到仓库，请检查网络或手动填写 data.ts")
    json.dump(
        {"source": URL, "projects": repos},
        open(a.out, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )
    print(f"已抓取 {len(repos)} 个仓库 -> {a.out}")
    for p in repos:
        print(f"  #{p['repo']}  +{p['weekStars']}  ({p['lang']})")


if __name__ == "__main__":
    main()
