# video-publish-pack

一次制作、多平台适配的视频发布物料生成 Skill。作为 [social-auto-upload](https://github.com/dreammis/social-auto-upload) 的**文案适配层**：发布执行交给 `sau` CLI，本 Skill 决定"每个平台发什么文案"。

## 解决什么问题

social-auto-upload 支持 18 个平台，但要求调用者自己提供 `--title / --desc / --tags`。一条视频要发十几个平台时，标题字数、描述结构、标签文化各不相同：

- 小红书标题 20 字封顶，抖音 60 字符、实践约 30 字，B站 80 字符，YouTube 100 字符；
- B站简介必填 ≥10 字、标签 ≤10 个，小红书话题可到 10 个，Instagram hashtag 已收紧到 5 个；
- 同一句"第一次自我介绍翻车了"，在小红书要种草口语，在知乎要信息密度，在虎扑要玩梗。

本 Skill 把这条视频按平台规则拆成多份文案，输出 `content-pack.json`（`xhsTitle`、`douyinTitle`、`bilibiliTitle`、`youtubeTitle` 等平台专用字段），逐平台喂给 CLI 即可。

## 结构

```
video-publish-pack/
├── SKILL.md                          # 定位、输入、内容包 schema、五步工作流、CLI 字段映射
├── references/
│   ├── platform-rules.md             # 16 平台标题/描述/标签硬限制总表（含置信度标注）
│   ├── platform-playbooks.md         # 分平台语气、标题公式、标签文化、CTA
│   ├── title-strategies.md           # 标题策略库（4 类公式 + 平台优先级）
│   └── subtitle-spec.md              # SRT/VTT 字幕规范
├── scripts/
│   └── validate_pack.py              # 内容包校验器（字数/标签数/必填）
└── examples/
    └── mimi-debut/                   # 案例：一条 15s 视频 → 15 平台内容包
        ├── video-brief.md
        ├── content-pack.json
        ├── titles-by-platform.md
        ├── subtitles.srt
        └── subtitles.vtt
```

## 用法

```
给这条视频做多平台发布包：抖音、小红书、B站、视频号、YouTube
```

AI 会：提炼基础内容 → 按 `platform-rules.md` 逐平台改写 → 输出 `content-pack.json` → 运行 `validate_pack.py` 校验 → 交付对照表。

生成后可直接消费：

```bash
python scripts/validate_pack.py content-pack.json

sau douyin upload-video --account creator --file videos/demo.mp4 \
  --title "<douyinTitle>" --desc "<douyinDesc>" --tags "tag1,tag2"

sau bilibili upload-video --account creator --file videos/demo.mp4 \
  --title "<bilibiliTitle>" --desc "<bilibiliDesc>" --tags "tag1,tag2" --tid 249
```

## 平台字段速查

| 平台 | 字段前缀 | 标题上限 |
|---|---|---|
| 小红书 | `xhsTitle` | 20 字 |
| 抖音 | `douyinTitle` | 60 字符 |
| B站 | `bilibiliTitle` | 80 字符 |
| 快手 | `kuaishouTitle` | 20 字（实践） |
| 视频号 | `tencentTitle` | 30 字（实践） |
| 百家号 | `baijiahaoTitle` | 30 字 |
| 微博 | `weiboTitle` | 30 字 |
| 虎扑 | `hupuTitle` | 4-40 字 |
| 知乎 | `zhihuTitle` | 5-50 字 |
| YouTube | `youtubeTitle` | 100 字符 |
| TikTok | `tiktokCaption` | 4000 字符（实践 300） |
| Instagram | `instagramCaption` | 2200 字符 |
| Facebook | `facebookTitle` | 255 字符 |
| 支付宝生活号 | `alipayTitle` | 30 字（建议） |
| 大鱼号 | `dayuTitle` | 20-40 字 |
| 雪球 | `xueqiuTitle` | 建议 20-30 字 |

完整规则与注意事项见 `references/platform-rules.md`。

## 说明

- 平台规则来源在 `platform-rules.md` 中逐条标注（官方 / 实践 / 待核实），平台政策会变，发布前以发布页为准。
- 内容包只生成用户点名平台的字段；不适配的平台（如雪球之于萌宠内容）可在 `notes` 中说明省略原因。
