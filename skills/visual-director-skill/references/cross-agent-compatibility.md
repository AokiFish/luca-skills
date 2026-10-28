# 跨 Agent 兼容性

本 Skill 面向"支持 `SKILL.md` 的 Agent/编码助手"设计。它不调用任何平台的私有 API，所有生成能力都通过"当前 Agent 原生能力"这一抽象路由，因此可被 WorkBuddy、Claude、Codex、Cursor 等任意支持 Skill 机制的宿主加载。

## 1. Frontmatter 规范

`SKILL.md` 顶部 YAML 至少包含：

```yaml
---
name: visual-director
description: "一句话说明触发场景与能力边界，足够让 Agent 判断何时启用本 Skill。"
version: "1.0.0"
---
```

- `name`：小写、连字符分隔，与文件夹名一致；
- `description`：写清**触发条件**（什么任务用）、**能力范围**与**不做什么**，避免过窄或过宽。本 Skill 的 description 已覆盖时尚/产品/品牌/社媒/短视频与纯分析场景，并声明"不编造未证实事实"；
- `version`：语义化版本，便于回归与迭代。

## 2. 不依赖私有 API

- 所有"生成图像/视频"的指令都描述为"使用当前 Agent 已提供的原生生成能力"；
- 不出现具体供应商名、模型名或平台专属端点；
- 若宿主未提供生成能力，Skill 退化为"交付提示词 + 制作包"，并明确标注未实际生成——这一退化路径内置于 [prompt-compilation.md](prompt-compilation.md)。

## 3. 多平台安装目录约定

将 `visual-director-skill` 文件夹放入对应 Agent 的 Skills 目录：

| 宿主 | 常见 Skills 目录 |
|---|---|
| WorkBuddy | 用户级 `~/.workbuddy/skills/` 或项目级 `.workbuddy/skills/` |
| Claude（CLI/Desktop） | `~/.claude/skills/` 或项目 `.claude/skills/` |
| Codex | `~/.codex/skills/` 或项目本地依赖 |
| Cursor | `.cursor/skills/` 或用户级 skills 目录 |
| 其他 | 查阅对应 Agent 的 Skill 安装文档，或直接把本目录作为项目本地依赖，在任务中显式让 Agent 读取 `SKILL.md` |

## 4. 触发写法

在任务中显式调用最稳妥：

```text
使用 visual-director，根据这张参考图制作一组写实的时尚图片。
```

或在支持 `$skill` 引用的宿主中使用符号引用（如 `$visual-director`）。description 已设计为可被 Agent 自动匹配：涉及"视觉诊断、创意方向、AI 图像/视频制作、分镜、质量修正"的任务应优先启用本 Skill。

## 5. 可选：宿主接口描述

若宿主要求提供 Skill 的展示元数据（如显示名、默认提问），可新增 `agents/interface.yaml` 之类文件，但内容必须与上述"原生能力路由"一致——不得在其中硬编码供应商。该文件为可选，缺失不影响核心功能。
