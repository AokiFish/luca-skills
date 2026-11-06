#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""扫描本地 Skill 根目录，输出 name / description 清单（Markdown 表）。

用法:
    python scripts/list_skills.py
    python scripts/list_skills.py --root "D:\self-media\luca-skills\skills" --root "C:\...\.user_skills"
    python scripts/list_skills.py --json
"""

import argparse
import json
import os
import re
import sys

DEFAULT_ROOTS = [
    r"D:\self-media\luca-skills\skills",
    os.path.expandvars(r"%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills"),
]

NAME_RE = re.compile(r"^name:\s*(.+?)\s*$")
DESC_RE = re.compile(r"^description:\s*(.+?)\s*$")


def parse_frontmatter(path):
    name, desc = None, None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[:120]
    except OSError:
        return None, None
    in_fm = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            in_fm = not in_fm
            continue
        if not in_fm:
            continue
        m = NAME_RE.match(line)
        if m and not name:
            name = m.group(1).strip("\"'")
        m = DESC_RE.match(line)
        if m and not desc:
            raw = m.group(1).strip()
            if raw in (">", ">-", ">+", "|", "|-", "|+"):
                collected = []
                for nxt in lines[idx + 1:]:
                    if not nxt.strip():
                        collected.append("")
                        continue
                    if nxt.startswith(" ") or nxt.startswith("\t"):
                        collected.append(nxt.strip())
                    else:
                        break
                desc = " ".join(x for x in collected if x).strip()
            else:
                desc = raw.strip("\"'")
    return name, desc


def scan(roots):
    rows = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            skill_md = os.path.join(root, entry, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue
            name, desc = parse_frontmatter(skill_md)
            rows.append({
                "name": name or entry,
                "dir": entry,
                "description": desc or "",
                "path": os.path.abspath(os.path.join(root, entry)),
                "root": os.path.abspath(root),
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-desc", type=int, default=90)
    args = ap.parse_args()

    roots = args.root or DEFAULT_ROOTS
    rows = scan(roots)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    if not rows:
        print("未找到任何 Skill，请检查 --root 路径。")
        return 1

    print("| Skill | 目录 | 说明 |")
    print("|---|---|---|")
    for r in rows:
        d = r["description"].replace("|", "\\|")
        if len(d) > args.max_desc:
            d = d[:args.max_desc] + "…"
        print(f"| {r['name']} | {r['dir']} | {d} |")
    print(f"\n共 {len(rows)} 个 Skill（根目录: {', '.join(roots)}）")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
