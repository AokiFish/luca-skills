# Luca Skills：跨 Agent 更新接入包

本方案面向 GitHub 仓库 `AokiFish/luca-skills`，以仓库现有的 `skills/` 目录为 Skill 集合目录，不要求绑定 WorkBuddy、Codex 或某个特定 Agent。

## 设计原则

- Skill 内容仍然由 GitHub 仓库统一发布。
- 使用开源生态的 `vercel-labs/skills` CLI 负责发现、安装记录、远端变化检测和更新。
- 本仓库不为每个 Skill 各自编写更新器。
- 检查与安装分开：先检查，再向用户展示检查结果并询问；只有明确输入 `y` 才执行更新。
- 不自动删除用户自己安装的其他 Skill。
- 不把宿主的 Skill 目录硬编码到仓库中。安装位置由 CLI 按用户选择的 Agent 决定。

## 需要的环境

- Node.js 22.20 或更高版本（按 Vercel Skills CLI 当前文档要求）。
- 网络访问 GitHub。
- 至少一个 Vercel Skills CLI 支持的 Agent。

## 从仓库安装

先列出仓库中可发现的 Skill：

```bash
npx skills add AokiFish/luca-skills --list
```

安装整个仓库中可发现的 Skill：

```bash
npx skills add AokiFish/luca-skills
```

也可以在交互界面中只选择需要的 Skill 和目标 Agent。第一次安装建议不要加 `-y`，以便检查选择。

若只想安装某一个 Skill，先执行 `--list` 读取真实 Skill 名称，再执行：

```bash
npx skills add AokiFish/luca-skills --skill "这里填写实际 Skill 名称"
```

如果该 CLI 在当前版本中没有自动发现 `skills/` 下的内容，可以用官方支持的目录 URL 逐个安装，例如：

```bash
npx skills add https://github.com/AokiFish/luca-skills/tree/main/skills/实际目录名
```

不要猜目录名；先用 `--list` 或 GitHub 页面确认。

## 检查并确认更新

交互式跨平台入口：

```bash
node scripts/luca-update.mjs
```

它会先运行 `npx skills check` 并显示检查结果，然后询问是否运行更新命令。输入 `y` 才会执行 `npx skills update`；其他输入都会取消。

也可以直接使用 CLI：

```bash
npx skills check
npx skills update
```

更新命令不加 `-y`，保留 CLI 的交互行为。

## 自动检查说明

Skill 本身不会常驻后台。若要自动检查，需要由用户的操作系统、Agent 宿主或定时器触发 `npx skills check`。这个触发器可以独立于 WorkBuddy/Codex；具体配置取决于用户使用的操作系统。

本接入包提供手动检查与确认入口，不会擅自安装，也不会伪装成已经配置了后台通知。定时任务只应运行检查命令；不要把 `npx skills update -y` 放进无人值守任务。

## 维护者发布流程

1. 在仓库 `skills/` 下新增或修改对应 Skill 目录。
2. 确保每个 Skill 目录包含 `SKILL.md`，并检查相对路径、引用资源和脚本。
3. 在 GitHub 提交并推送。
4. 用户运行检查入口，确认后更新。

不要求为每个 Skill 新建更新脚本。未来如需变更日志，可以为每个 Skill 在 `SKILL.md` 中维护简短的版本/变更说明，或在仓库发布页记录版本。

## 边界与安全

- 这是对 Vercel Skills CLI 的薄封装，不是新的包管理器。
- CLI 能管理的 Agent 目录以其官方支持列表为准；不支持的 Agent 仍可手动复制 Skill，但不会因此自动获得更新追踪。
- 手动复制安装的 Skill，可能不会出现在 CLI 的安装锁文件中。要获得 CLI 更新能力，建议先通过 CLI 安装并选择目标 Agent。
- 运行更新前请阅读 CLI 检查输出。Skill 内容可能包含提示词、脚本或其他可执行资源，更新应视作信任代码变更。
