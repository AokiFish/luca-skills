#!/usr/bin/env python3
"""从 data.ts 自动生成「标题 + 说明」markdown，供发短视频平台使用。

用法：
    python gen_copy.py --data src/GithubWeekly/data.ts --outdir out/github-weekly-YYYY-MM-DD

输出：<date>.md（含标题、1～5 项目说明、合计星数结尾、英文推广段）。

说明：标题亮点与每个项目的介绍直接从 desc/points 提炼，措辞是"可编辑草稿"，
      agent 交付前可按 references/output-copy.md 的模板再润色。
"""
import argparse
import datetime
import os
import re


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_weeks(src):
    lab = re.search(r'export const WEEK_LABEL\s*=\s*"([^"]*)"', src)
    short = re.search(r'export const WEEK_SHORT\s*=\s*"([^"]*)"', src)
    word = re.search(r'export const WEEK_WORD\s*=\s*"([^"]*)"', src)
    return (
        lab.group(1) if lab else "",
        short.group(1) if short else "",
        word.group(1) if word else "本周",
    )


def extract_projects(src):
    blocks = re.findall(r"\{\s*rank: (\d+),.*?url: \"([^\"]+)\",", src, re.S)
    names = re.findall(r"name: \"([^\"]+)\",", src)
    descs = re.findall(r"desc: \"([^\"]*)\",", src)
    points = re.findall(r"points: \[(.*?)\],", src, re.S)
    tags = re.findall(r"tags: \[(.*?)\],", src, re.S)
    stars = [int(x) for x in re.findall(r"weekStars: (\d+)", src)]

    def clean_list(s):
        return [x.strip() for x in re.findall(r"\"([^\"]*)\"", s)]

    projects = []
    for i in range(len(names)):
        projects.append(
            {
                "rank": i + 1,
                "name": names[i],
                "desc": descs[i] if i < len(descs) else "",
                "points": clean_list(points[i]) if i < len(points) else [],
                "tags": clean_list(tags[i]) if i < len(tags) else [],
                "url": blocks[i][1] if i < len(blocks) else "",
                "weekStars": stars[i] if i < len(stars) else 0,
            }
        )
    return projects


def build_title(week_short, projects):
    highs = "、".join(p["desc"] for p in projects if p["desc"])
    return f"Github 本周开源热榜：{highs}：{week_short} Top5"


def build_lines(projects):
    lines = []
    for p in projects:
        intro = "，".join(p["points"][:2]) if p["points"] else ""
        body = f"{p['desc']}，{intro}" if intro else p["desc"]
        lines.append(
            f"{p['rank']}. **{p['name']}**：{body}。链接：[https://{p['url']}](https://{p['url']})"
        )
    return lines


def build_tail(week_short, projects):
    tagset = []
    for p in projects:
        for t in p["tags"]:
            if t not in tagset:
                tagset.append(t)
    total = sum(p["weekStars"] for p in projects)
    area = "、".join(tagset) if tagset else "AI 开源生态"
    wan = f"{total/10000:.1f}" if total >= 10000 else str(total)
    return (
        f"{week_short} Github 开源热榜 Top 5，覆盖 {area}，"
        f"这五个项目本周合计涨了 {wan} 万星。"
    )


EN_SNIPPET = (
    "Hey, foreign friends! If you want to understand the content of this video more easily, "
    "you can try the CCDub extension. It provides accurate translation and dubbing with "
    "ChatGPT, helping you easily understand every part. Click the link below to install it now! "
    "https://dub.qhkly.com/install.html"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()

    src = read(a.data)
    week_label, week_short, week_word = extract_weeks(src)
    projects = extract_projects(src)
    if not projects:
        raise SystemExit("未解析到项目，请检查 data.ts")

    md = [
        f"# {build_title(week_short, projects)}",
        "",
        "\n\n".join(build_lines(projects)),
        "",
        build_tail(week_short, projects),
        "",
        EN_SNIPPET,
        "",
    ]
    content = "\n".join(md)

    os.makedirs(a.outdir, exist_ok=True)
    out = os.path.join(a.outdir, f"github-weekly-{a.date}.md")
    open(out, "w", encoding="utf-8").write(content)
    print(f"已生成文案 -> {out}")
    print(f"  周: {week_label or week_short}; 项目: {len(projects)}; 合计星数: {sum(p['weekStars'] for p in projects)}")


if __name__ == "__main__":
    main()
