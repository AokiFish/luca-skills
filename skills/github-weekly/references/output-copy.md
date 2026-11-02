# 标题与说明文案模板

用于发 YouTube Shorts / 小红书 / 公众号。可用 `scripts/gen_copy.py` 从 `data.ts` 自动生成草稿，再按本模板润色标题亮点与说明措辞。

## 标题

```
Github 本周开源热榜：{亮点1}、{亮点2}、{亮点3}、{亮点4}、{亮点5}：{WEEK_SHORT} Top5
```

- 亮点从每个项目 desc / points 提炼成 2-4 字短语（如 "AI 逆向工程""本地语音克隆""多 Agent 工作台"），不要照抄整句 desc。
- `WEEK_SHORT` 取 `data.ts`（如 "11月第1周"）。

## 说明正文

```
1｜{name}：{2-3 句话：是什么 + 给谁用 + 为什么火}。链接：[https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})
2｜{name}：{...}。链接：[https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})
3｜{name}：{...}。链接：[https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})
4｜{name}：{...}。链接：[https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})
5｜{name}：{...}。链接：[https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})

{WEEK_SHORT} Github 开源热榜 Top 5，覆盖 {领域1}、{领域2}、{领域3} 和 {领域4}，这五个项目本周合计涨了 {合计万星} 万星。

Hey, foreign friends! If you want to understand the content of this video more easily, you can try the CCDub extension. It provides accurate translation and dubbing with ChatGPT, helping you easily understand every part. Click the link below to install it now! https://dub.qhkly.com/install.html
```

## 规则

- 链接用 markdown 格式 `[https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})`（`data.ts` 的 `url` 已含 `github.com/`，直接 `https://{url}`）。
- 说明每个项目 2-3 句，说清"是什么 + 给谁用 + 为什么火"，不要过长。
- 结尾一句总结覆盖领域 + 合计星数（= `PROJECTS.weekStars` 求和，脚本已算）。
- 英文 CCDub 推广段固定附带（匹配用户模板）。
