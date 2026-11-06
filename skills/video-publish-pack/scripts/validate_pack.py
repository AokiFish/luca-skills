#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 video-publish-pack 内容包，按各平台标题/描述/标签限制输出报告。

同时校验双语字幕结构（zh/en）与 subtitleByPlatform 平台映射。

用法:
    python scripts/validate_pack.py content-pack.json

退出码:
    0 = 全部通过（可能有 warning）
    1 = 存在 error（超限/缺必填/字幕映射错误）
    2 = 文件/JSON 读取失败
"""

import json
import sys

# title_max / title_soft / title_min / desc_max / desc_min / tags_max
# soft 为实践建议上限，超了只告警；max 为硬限制，超了报错。
PLATFORMS = {
    "douyin":    {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 60,  "title_soft": 30, "tags_max": 5,  "desc_max": 500},
    "xhs":       {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 20,  "tags_max": 10, "desc_max": 1000},
    "bilibili":  {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 80,  "title_soft": 30, "desc_min": 10, "desc_max": 249, "tags_max": 10},
    "kuaishou":  {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 20,  "tags_max": 3,  "desc_max": 50},
    "tencent":   {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 30,  "tags_max": 3,  "desc_max": 200},
    "baijiahao": {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 30,  "title_soft": 18, "tags_max": 3, "desc_max": 100},
    "weibo":     {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 30,  "tags_max": 3},
    "hupu":      {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 40,  "title_min": 4,  "tags_max": 4},
    "zhihu":     {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 50,  "title_min": 5,  "desc_max": 300, "tags_max": 10, "tags_min": 3},
    "youtube":   {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 100, "desc_max": 5000, "tags_max": 8},
    "tiktok":    {"field": "Caption", "tags": "Tags", "title_max": 4000, "title_soft": 300, "tags_max": 5},
    "instagram": {"field": "Caption", "tags": "Tags", "title_max": 2200, "title_soft": 2200, "tags_max": 5},
    "facebook":  {"field": "Title", "desc": "Desc", "tags": None, "title_max": 255, "desc_max": 63206},
    "alipay":    {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 30,  "title_soft": 30, "tags_max": 3, "desc_max": 100},
    "dayu":      {"field": "Title", "desc": "Desc", "tags": "Tags", "title_max": 40,  "tags_max": 4,  "desc_max": 100},
    "xueqiu":    {"field": "Title", "desc": None, "tags": None, "title_max": 30,  "title_soft": 30},
}

OVERSEAS = {"youtube", "tiktok", "instagram", "facebook"}


def clen(text):
    """按字符数统计（中文/英文/标点均按 1 个字符）。"""
    return len(text.strip()) if isinstance(text, str) else 0


def generated_platforms(content):
    return [name for name, cfg in PLATFORMS.items() if (name + cfg["field"]) in content]


def check_platform(name, cfg, content):
    """返回 (errors, warnings)。"""
    errors, warnings = [], []
    title_key = name + cfg["field"]
    title = content.get(title_key)
    if title is None:
        return errors, warnings  # 该平台未生成，跳过

    n = clen(title)
    if n == 0:
        errors.append(f"{title_key} 为空")
    if n > cfg["title_max"]:
        errors.append(f"{title_key} {n} 字符 > 上限 {cfg['title_max']}")
    elif "title_soft" in cfg and n > cfg["title_soft"]:
        warnings.append(f"{title_key} {n} 字符 > 建议 {cfg['title_soft']}")
    if "title_min" in cfg and n < cfg["title_min"]:
        errors.append(f"{title_key} {n} 字符 < 下限 {cfg['title_min']}")

    if cfg.get("desc"):
        desc_key = name + cfg["desc"]
        desc = content.get(desc_key, "")
        dn = clen(desc)
        if cfg.get("desc_min") and dn < cfg["desc_min"]:
            errors.append(f"{desc_key} {dn} 字符 < 必填下限 {cfg['desc_min']}")
        if cfg.get("desc_max") and dn > cfg["desc_max"]:
            errors.append(f"{desc_key} {dn} 字符 > 上限 {cfg['desc_max']}")

    if cfg.get("tags"):
        tags_key = name + cfg["tags"]
        tags = content.get(tags_key, [])
        if isinstance(tags, list):
            if cfg.get("tags_max") and len(tags) > cfg["tags_max"]:
                errors.append(f"{tags_key} {len(tags)} 个 > 上限 {cfg['tags_max']}")
            if cfg.get("tags_min") and len(tags) < cfg["tags_min"]:
                errors.append(f"{tags_key} {len(tags)} 个 < 下限 {cfg['tags_min']}")

    return errors, warnings


def check_subtitles(pack, content):
    """校验双语字幕结构与平台映射，返回 (errors, warnings)。"""
    errors, warnings = [], []
    subs = pack.get("subtitles")
    if subs is None:
        return errors, warnings

    if not isinstance(subs, dict):
        errors.append("subtitles 必须是对象")
        return errors, warnings

    gen = generated_platforms(content)

    # 旧版单语言结构：{ "srt": "...", "vtt": "..." }
    if "srt" in subs and "vtt" in subs and not any(k in subs for k in ("zh", "en")):
        if any(p in OVERSEAS for p in gen):
            warnings.append("subtitles 为单语言结构；已生成海外平台，建议提供 subtitles.en.* 双语字幕")
        return errors, warnings

    langs = {}
    for lang, item in subs.items():
        if not isinstance(item, dict):
            errors.append(f"subtitles.{lang} 必须是含 srt/vtt 的对象")
            continue
        if not item.get("srt") or not item.get("vtt"):
            errors.append(f"subtitles.{lang} 缺少 srt 或 vtt 文件名")
            continue
        langs[lang] = item

    if not langs:
        errors.append("subtitles 未包含任何语言条目（应为 zh / en 对象）")
        return errors, warnings

    mapping = pack.get("subtitleByPlatform")
    if mapping is None:
        if gen:
            warnings.append("未声明 subtitleByPlatform，发布环节无法按平台自动选字幕语言")
        return errors, warnings

    if not isinstance(mapping, dict):
        errors.append("subtitleByPlatform 必须是对象")
        return errors, warnings

    for p in gen:
        if p not in mapping:
            warnings.append(f"subtitleByPlatform 缺少平台 {p}（将回退默认语言）")
            continue
        lang = mapping[p]
        if lang not in langs:
            errors.append(f"subtitleByPlatform.{p} = {lang}，但 subtitles 中没有该语言")
            continue
        expect = "en" if p in OVERSEAS else "zh"
        if lang != expect:
            warnings.append(f"subtitleByPlatform.{p} = {lang}，与默认规则（{expect}）不一致，请确认是用户指定")
    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/validate_pack.py content-pack.json")
        return 2
    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            pack = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[读取失败] {path}: {e}")
        return 2

    content = pack.get("content", {})
    if not isinstance(content, dict) or not content:
        print("[错误] 内容包缺少 content 对象")
        return 2

    total_err, total_warn = 0, 0
    print(f"=== video-publish-pack 内容包校验: {path} ===")
    for name, cfg in PLATFORMS.items():
        title_key = name + cfg["field"]
        if title_key not in content:
            continue
        errors, warnings = check_platform(name, cfg, content)
        if errors:
            total_err += len(errors)
            print(f"[{name}] ERROR")
            for e in errors:
                print(f"    - {e}")
        elif warnings:
            total_warn += len(warnings)
            print(f"[{name}] WARN")
            for w in warnings:
                print(f"    - {w}")
        else:
            print(f"[{name}] OK")

    sub_errors, sub_warnings = check_subtitles(pack, content)
    if sub_errors:
        total_err += len(sub_errors)
        print("[subtitles] ERROR")
        for e in sub_errors:
            print(f"    - {e}")
    elif sub_warnings:
        total_warn += len(sub_warnings)
        print("[subtitles] WARN")
        for w in sub_warnings:
            print(f"    - {w}")
    else:
        if pack.get("subtitles") is not None:
            langs = [k for k, v in (pack.get("subtitles") or {}).items() if isinstance(v, dict)]
            if langs:
                print(f"[subtitles] OK（语言: {', '.join(langs)}）")

    missing = [k for k, v in PLATFORMS.items() if (k + v["field"]) not in content]
    print(f"\n已生成平台: {len(generated_platforms(content))} 个；未生成: {', '.join(missing) if missing else '无'}")
    print(f"结果: {total_err} 个 error, {total_warn} 个 warning")
    return 1 if total_err else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
