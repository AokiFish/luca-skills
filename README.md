# luca-skills

跨 Agent 通用的视觉创作 Skill 集合，由 GitHub 统一发布，不绑定任何单一 Agent 或模型。

## 包含的 Skill

| Skill | 用途 | 目录 |
|---|---|---|
| **visual-director** | 把参考图/视频/一句话创意转化为可执行视觉方案：视觉诊断、创意方向、生成提示词、质量检查与定向修正。适用于时尚编辑、产品/品牌视觉、社媒、短视频分镜与 AI 图像/视频制作。 | [`skills/visual-director-skill`](skills/visual-director-skill) |
| **video-link-to-prompt** | 分析视频链接或上传视频，逐镜头拆解创意机制，产出可跨模型复用的视频生成提示词、分镜表与模型专设参数。 | [`skills/video-link-to-prompt-skill`](skills/video-link-to-prompt-skill) |
| **video-music-extract** | 从 B 站 / YouTube 等任意视频链接抽取音乐 mp3，用一个"意图"参数控制是否保留人声：pure（默认，自动去人声）、all（保留原唱+配音）、chorus/C（保留合唱/衬底"啊"人声）。 | [`skills/video-music-extract-skill`](skills/video-music-extract-skill) |
| **music-instrument-analysis** | 上传或链接一段音乐，用 YAMNet(ONNX) 客观乐器概率 + 频谱特征 + 音乐学知识识别乐器组成，讲解每种乐器的适用场景与最佳搭配，并支持时间轴分段配器表。 | [`skills/music-instrument-analysis-skill`](skills/music-instrument-analysis-skill) |

每个 Skill 目录均含 `SKILL.md`（核心路由 + 约束）、`scripts/`（本地可执行脚本），多数含 `assets/`、`requirements.txt` 与 `README.md`；部分含 `references/`（按需加载的详细规则）与 `templates/`（产出模板）。

## 安装

使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 从本仓库发现并安装：

```bash
npx skills add AokiFish/luca-skills --list   # 先查看可安装的 Skill
npx skills add AokiFish/luca-skills          # 安装全部可发现 Skill
```

只安装某一个：

```bash
npx skills add AokiFish/luca-skills --skill "实际 Skill 名称"
```

> 目录名以 `--list` 或 GitHub 页面为准，不要凭记忆猜测。

## 更新

仓库附带一个跨平台、先检查再明确确认的更新入口（见 [`luca-skills-universal-update`](luca-skills-universal-update)）：

```bash
node luca-skills-universal-update/scripts/luca-update.mjs
```

它会先运行 `npx skills check` 展示结果，只有你输入 `y` 才会执行 `npx skills update`。设计原则、安全边界与维护者发布流程详见该目录的 `README.md`。

## 维护约定

- Skill 内容统一由本仓库发布，不要求绑定 WorkBuddy / Codex / 其他特定 Agent。
- 生成能力统一走"当前 Agent 原生能力"路由，不硬编码任何供应商或模型。
- 提交信息用英文，避免 Windows Git Bash 中文乱码。
- `.workbuddy/` 为本地项目数据，已加入 `.gitignore`，不纳入版本控制。

## License

见 [LICENSE](LICENSE)。
