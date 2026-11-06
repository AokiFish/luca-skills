#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""用抖音 cookie 打开创作者后台作品管理页，打印状态信息并截图。

用法（在项目根执行，使用项目 venv 的 python）:
    python scripts/verify_douyin_post.py --cookie "cookies\douyin_mimi.json" --out "_verify_post.png"

注意：当前环境缺 chromium headless shell，脚本默认有头启动；如环境完整可加 --headless。
"""

import argparse
import asyncio
import json
import os
import sys

from patchright.async_api import async_playwright

DEFAULT_URL = "https://creator.douyin.com/creator-micro/content/manage"


def load_cookies(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cookies = data.get("cookies") if isinstance(data, dict) else data
    clean = []
    for c in cookies:
        item = {"name": c.get("name"), "value": c.get("value"),
                "domain": c.get("domain"), "path": c.get("path", "/")}
        if c.get("expires") and c.get("expires") > 0:
            item["expires"] = c["expires"]
        for key in ("httpOnly", "secure"):
            if key in c:
                item[key] = c[key]
        if c.get("sameSite") in ("Strict", "Lax", "None"):
            item["sameSite"] = c["sameSite"]
        clean.append(item)
    return clean


async def main(args):
    cookies = load_cookies(args.cookie)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=args.headless,
            channel="chromium",
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()
        try:
            await page.goto(args.url, timeout=60000, wait_until="domcontentloaded")
        except Exception as e:
            print("GOTO_ERROR:", e)
        await page.wait_for_timeout(args.wait_ms)
        print("TITLE:", await page.title())
        print("URL:", page.url)
        try:
            body = await page.inner_text("body")
            print("BODY_HEAD:")
            print(body[:2000])
        except Exception as e:
            print("BODY_ERROR:", e)
        await page.screenshot(path=args.out, full_page=False)
        print("SHOT:", os.path.abspath(args.out))
        await browser.close()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--cookie", required=True)
    ap.add_argument("--out", default="_verify_post.png")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--wait-ms", type=int, default=8000)
    ap.add_argument("--headless", action="store_true")
    asyncio.run(main(ap.parse_args()))
