# luca-skills

跨 Agent 通用的视觉创作 Skill 集合，由 GitHub 统一发布，不绑定任何单一 Agent 或模型。

## 包含的 Skill

| Skill | 用途 | 目录 |
|---|---|---|
| **visual-director** | 把参考图/视频/一句话创意转化为可执行视觉方案：视觉诊断、创意方向、生成提示词、质量检查与定向修正。适用于时尚编辑、产品/品牌视觉、社媒、短视频分镜与 AI 图像/视频制作。 | [`skills/visual-director`](skills/visual-director) |
| **twin-prank-fix** | 双胞胎爆款短视频的视觉语法创意设计师：把「绅士拐杖不经意行善」的病毒格式改写为「一个恶作剧、一个善后」的双胞胎反差动态，提供视觉语法框架、道具逻辑工坊、双生人设系统与 46s 节拍分镜蓝图。 | [`skills/twin-prank-fix`](skills/twin-prank-fix) |
| **video-link-to-prompt** | 分析视频链接或上传视频，逐镜头拆解创意机制，产出可跨模型复用的视频生成提示词、分镜表与模型专设参数。 | [`skills/video-link-to-prompt`](skills/video-link-to-prompt) |
| **video-downloader** | 给定任一主流平台视频链接（YouTube、X/Twitter、Bilibili、抖音、小红书、TikTok、微博等），用 yt-dlp 下载为本地文件。支持 Windows `--auto-proxy` 自动检测系统代理并按域名分流。 | [`skills/video-downloader`](skills/video-downloader) |
| **video-mix** | 把一个目录下的多段短视频按文件名顺序拼接成完整长视频，按画面情绪重新生成配乐；输出 H.264+AAC faststart，可直接上传 X/抖音/微信。 | [`skills/video-mix`](skills/video-mix) |
| **video-music-extract** | 从 B 站 / YouTube 等任意视频链接抽取音乐 mp3，用一个"意图"参数控制是否保留人声：pure（默认，自动去人声）、all（保留原唱+配音）、chorus/C（保留合唱/衬底"啊"人声）。 | [`skills/video-music-extract`](skills/video-music-extract) |
| **music-instrument-analysis** | 上传或链接一段音乐，用 YAMNet(ONNX) 客观乐器概率 + 频谱特征 + 音乐学知识识别乐器组成，讲解每种乐器的适用场景与最佳搭配，并支持时间轴分段配器表。 | [`skills/music-instrument-analysis`](skills/music-instrument-analysis) |
| **video-publish-pack** | 一次制作、多平台适配的视频发布物料生成器：为同一视频按抖音、小红书、B站、快手、视频号、YouTube 等 16 个平台的标题字数、描述结构、标签规则生成内容包（`xhsTitle`、`douyinTitle`、`bilibiliTitle` 等平台专用字段），附内容包校验脚本与 SRT/VTT 字幕规范，作为 social-auto-upload 的文案适配层。 | [`skills/video-publish-pack`](skills/video-publish-pack) |
| **sau-publish** | 发布执行层：用 social-auto-upload 的 `sau` CLI 把视频/图文真正发到抖音、小红书、B站、快手、视频号、YouTube 等平台；含 Windows 安装踩坑、扫码登录、短信验证码处理、内容包转命令脚本与发布结果核验脚本。 | [`skills/sau-publish`](skills/sau-publish) |
| **task-conductor** | 多 Skill 任务的编排总指挥：拆任务图、选 Skill、定依赖与输入输出契约、设验收标准并汇总；自己不上场执行，只做编排与只读验收。 | [`skills/task-conductor`](skills/task-conductor) |
| **deep-article-production** | 热点人物深度文章生产流程：先过热点门槛（14 天内原发病毒内容 + 本人第一方实用方法），再出核查底稿，写方法优先母版，经独立 Checker 验收后按已验证路线发表，24 小时/7 天回收转发数据。无最近热点不写，哪怕是卡帕西。 | [`skills/deep-article-production`](skills/deep-article-production) |
| **agentrun-setup** | 安装 Parcha AgentRun 平台并跑通第一个 agent：学习闭环（每轮提议 notes/skills/workflows，经检查+评分后 commit，下轮接着用）、持久执行、审批与花销上限、统一控制台；面向 Claude Code / Codex / OpenCode / pi。 | [`skills/agentrun-setup`](skills/agentrun-setup) |
| **smooth-transitions** | 切换平滑规则：轮播、标签页、滚动行、灯箱等一切视图切换必须带过渡动画，禁止瞬跳；小切换 90–200ms，整窗滑动 200–300ms，ease-out。 | [`skills/smooth-transitions`](skills/smooth-transitions) |
| **three-prohibitions** | 三禁：禁自作聪明、禁图省事、禁重要更改不交代。 | [`skills/three-prohibitions`](skills/three-prohibitions) |
| **delegation-contract** | 传达铁律：brief 必须带完整规格原文 + 独立验收。 | [`skills/delegation-contract`](skills/delegation-contract) |
| **effect-improvement** | 效果改进法：先解析再选策略，maker ≠ checker，对照真高质量素材迭代。 | [`skills/effect-improvement`](skills/effect-improvement) |
| **skill-sedimentation** | 经验第一次做对/犯错就写 skill；先修 bug 再写 skill。 | [`skills/skill-sedimentation`](skills/skill-sedimentation) |
| **troubleshooting-playbook** | 故障排查：端到端实测验收、先查日志、架构怀疑、官方模板优先。 | [`skills/troubleshooting-playbook`](skills/troubleshooting-playbook) |
| **login-discipline** | 登录负担纪律：最小化身份步骤、单会话、已登录 Google 点选、不存 Google 密码。 | [`skills/login-discipline`](skills/login-discipline) |
| **browser-session-discipline** | 标签页纪律：用完即关、同站最多 2 个、只读核查优先 curl。 | [`skills/browser-session-discipline`](skills/browser-session-discipline) |
| **x-post-reading** | X 推文优先 fxtwitter 读，必须带 Accept 头。 | [`skills/x-post-reading`](skills/x-post-reading) |
| **orchestration** | 指挥架构：单指挥官 + 窄编制 + maker ≠ checker + 涌现式分工。 | [`skills/orchestration`](skills/orchestration) |
| **space-network-wiring** | 空间节点连线：空间独立、咪咪做衔接、P1–P3 已落地。 | [`skills/space-network-wiring`](skills/space-network-wiring) |
| **identity-pose-separation** | 身份姿势彻底分开：姿势库只用统一白模、人物库单存身份。 | [`skills/identity-pose-separation`](skills/identity-pose-separation) |
| **unified-data-standard** | 统一数据标准 v1：7 Studio ID 前缀 + 共享素材索引 + 字段级分离。 | [`skills/unified-data-standard`](skills/unified-data-standard) |
| **mimi-visual-system** | 咪咪视觉系统 v1.1：双极绿、封面主角优先、Rule F。 | [`skills/mimi-visual-system`](skills/mimi-visual-system) |
| **wechat-publish-safety** | 公众号发布安全：文档导入路线、编辑器空保存 hazard、作者栏咪咪、群发 1 次上限。 | [`skills/wechat-publish-safety`](skills/wechat-publish-safety) |
| **x-operations** | X 运营 @mimiAIStudio：目标、回复铁律、引用铁律、三层筛、巡查制。 | [`skills/x-operations`](skills/x-operations) |
| **x-dashboard** | X AI 监控看板：6 栏 Top 5、收录门槛、7 天时效、晨晚两更。 | [`skills/x-dashboard`](skills/x-dashboard) |
| **en-prompt-first** | 生成入口中文先译英文再出图/视频。 | [`skills/en-prompt-first`](skills/en-prompt-first) |
| **kaggle-gpu** | Kaggle：模型挂数据集、Aoo 号、IC-Light 跑通、OOM 教训。 | [`skills/kaggle-gpu`](skills/kaggle-gpu) |
| **doubao-generation** | 豆包生成：文生/图生视频、图生图同身份换装、403 长期限制。 | [`skills/doubao-generation`](skills/doubao-generation) |
| **free-quota** | 免费额度雷达：只认四源、存疑标未核实、过期下架、资源分配规则。 | [`skills/free-quota`](skills/free-quota) |
| **no-fabrication** | 不编造：第一方证据或 nothing，数字/账号/日期须核实。 | [`skills/no-fabrication`](skills/no-fabrication) |
| **space-engineering** | 空间工程：Worker 不支持、分片、ir_version、深度只需一个模型、需存数据建全栈。 | [`skills/space-engineering`](skills/space-engineering) |
| **platform-topic-strategy** | 平台选题策略总纲：逐平台独立判定、禁一题打天下。 | [`skills/platform-topic-strategy`](skills/platform-topic-strategy) |
| **tiktok-viral-research** | TikTok 爆款调研：先调研后制作、数据给中文 + 排序、方向由数据定。 | [`skills/tiktok-viral-research`](skills/tiktok-viral-research) |
| **space-backup-sync** | Muse 空间 GitHub 备份：快照推送流程、凭证永不入库。 | [`skills/space-backup-sync`](skills/space-backup-sync) |
| **adaptation-checks** | 适配验收：标题字数脚本实测、hedge 须带归属动词。 | [`skills/adaptation-checks`](skills/adaptation-checks) |
| **secret-handling** | 密钥铁律：不用公开默认 UUID、只存 600 权限文件、不入库。 | [`skills/secret-handling`](skills/secret-handling) |
| **audit-read-only** | 分类审查只读：巡检只列疑似、不自动改数据。 | [`skills/audit-read-only`](skills/audit-read-only) |
| **video-production-workflow** | 视频制作工作流：museai-video、分镜表先行、每 10 秒一个任务。 | [`skills/video-production-workflow`](skills/video-production-workflow) |
| **report-results-only** | 汇报只说结果：分类统计、不堆文字、补光文字不超 2 行。 | [`skills/report-results-only`](skills/report-results-only) |

每个 Skill 目录均含 `SKILL.md`（核心路由 + 约束）、`scripts/`（本地可执行脚本），多数含 `assets/`、`requirements.txt` 与 `README.md`；部分含 `references/`（按需加载的详细规则）与 `templates/`（产出模板）。

**目录命名约定**：Skill 目录直接用 `<name>` 命名（如 `skills/visual-director/`），**不加 `-skill` 后缀** —— 已经在 `skills/` 目录下，无需重复说明。新建 Skill 时同样遵守。

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
