# Visual Director

一个面向 AI 视觉创作的**通用**导演型 Skill。它把参考图、视频或一句话创意，转化为可执行的视觉方案：完成视觉诊断、创意方向、生成提示词、质量检查与定向修正。默认偏向时尚/编辑摄影与短视频，但主题域、风格、画幅与生成方式都可独立配置，不绑定任何视频模型或生成平台。

当前版本：`1.0.0`

## 它解决什么问题

生成模型能产出漂亮画面，但视觉创作还需要回答更多问题：

- 参考图到底传达了什么，哪些该保留、哪些只是表面标签；
- 开头三秒（或第一帧）有没有真正抓住注意力；
- 产品/人物/品牌元素是否参与叙事因果，而不是最后突然贴片；
- 系列作品里角色身份与视觉语言是否一致；
- 生成失败后，能否只修证据指向的层，而不推翻已经成功的部分；
- 没有可用生成能力时，能否交付一份完整、可执行、不虚报的制作包。

`visual-director` 把这些判断编译为可执行规则，并通过 `evals/` 中的回归用例持续校验。

## 主要能力

- `单图 / 图片系列 / 短视频 / 分镜板 / 仅分析` 五种产出路由；
- 六个互不绑定的决策配置轴（产出类型、主题域、风格、画幅、生成方式、生成能力、数量节奏），不互相偷换；
- 参考图/视频的可见事实提取与情绪/意图解读，区分事实与解释；
- 单一核心视觉主张 + 最多三条机制不同的创意路线；
- 图片与视频的生产计划：构图、镜头表、素材职责、主体/产品/人物锁、时间轴事件结构；
- 按"当前 Agent 原生生成能力"路由的提示词编译，不硬编码供应商；
- 多维度质量检查与最多两轮定向修正；
- 成片复盘：区分成功层与失败层，只输出保留项、主修层与重试指令。

## 安装

### WorkBuddy / Claude / Codex / Cursor 等支持 SKILL.md 的 Agent

将 `visual-director-skill` 文件夹放进当前 Agent 的 Skills 目录（不同平台目录不同，见 [references/cross-agent-compatibility.md](references/cross-agent-compatibility.md)），或直接把本目录作为项目本地依赖，在任务中明确让 Agent 读取 `SKILL.md`。

### 最简单的使用方式

```text
使用 visual-director，根据这张参考图做一组写实的时尚图片。
```

或：

```text
使用 visual-director 分析这张图，提取可复用的视觉配方，暂时不要生成。
```

未说明配置时，Skill 会一次性确认七个互不绑定的配置轴（产出类型、主题域、风格、画幅、生成方式、生成能力、数量节奏），每项先给推荐理由。

## 设计结构

```text
输入受理与事实边界
  → 七个独立决策配置轴
  → 参考诊断（事实 / 解释分离）
  → 单一核心主张与三条差异路线
  → 图片 / 视频生产计划（素材职责、主体锁、时间轴）
  → 提示词编译（原生生成能力路由）
  → 多维度质量检查
  → 最多两轮定向修正
  → 文件包交付与成片复盘
```

核心路由保留在 `SKILL.md`，详细规则按需放在 `references/`；真实失败案例被压缩为 `evals/evals.json` 中的回归断言。输出模板见 `templates/`。

## 文件结构

```text
visual-director-skill/
├── SKILL.md                      # 核心路由与约束
├── README.md                     # 本文件
├── references/                   # 按需加载的详细规则
│   ├── intake-and-brief.md       # 受理、事实边界、配置轴、工作模式
│   ├── reference-diagnosis.md    # 图/视频诊断
│   ├── creative-direction.md     # 创意方向与视觉语言
│   ├── production-planning.md    # 生产计划、素材职责、主体锁、时间轴
│   ├── prompt-compilation.md     # 提示词编译与原生能力路由
│   ├── quality-control.md        # 质检维度与定向修正
│   ├── output-contract.md        # 交付契约与模板索引
│   └── cross-agent-compatibility.md  # 跨 Agent 兼容与安装
├── templates/                    # 交付模板
│   ├── creative-brief.md
│   ├── visual-recipe.md
│   ├── generation-prompts.md
│   ├── quality-report.md
│   ├── series-bible.md
│   └── video-storyboard.md
├── examples/
│   └── example-fashion-brief.md  # 示例工作产物
└── evals/
    └── evals.json                # 回归断言
```

## 边界

- 这是导演与提示词编译 Skill，不保证任何平台的生成效果、参数上限或商业可投放性；
- 精确 Logo、包装小字、价格、CTA、免责声明与播出级文案应由后期使用获批资产完成；
- 未经验证的功效、数据、认证和绝对化表达必须保留为 `【待补】`；
- 具体生成模型的实际能力可能因入口和时间变化，使用前请以当前平台为准。

## License

代码与文档使用 MIT License。第三方品牌、产品与商标不属于本许可证授权范围。
