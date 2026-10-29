# 交付契约

规定默认交付顺序与文件包结构。用户明确只要其中一项时，缩减交付。

## 一、对话内默认输出顺序

1. **Brief 判断**：已知信息、保守假设与 `【待补】`；
2. **生成配置**：分别写明产出类型、主题域、风格、画幅、生成方式、生成能力、数量节奏，以及各自理由；
3. **核心策略**：受众/用途、表达或商业目标、单一核心主张、视觉证明、目标感受；
4. **创意路线**：未选方向时给 3 条；已选时说明采用哪条及原因；
5. **执行单**：一句创意、视觉规则、表演/主体、摄影、光线、声音（若有）、主体与品牌出现规则；
6. **时间轴/镜头表**：每段写清画面事件、镜头观察、声音变化（若有）与商业/表达任务；
7. **可复制提示词**：放进独立代码块，只包含可执行指令，不混入分析；
8. **后期与交付清单**：Logo、字幕、法务小字、精确包装字样等应在后期完成的项目；
9. **风险与可调旋钮**：只保留 3–5 个真正会改变结果的变量。

## 二、文件包结构（有文件创建能力时）

在整洁的输出文件夹中创建：

- `01_creative_brief.md` —— 创意简报（模板见 [templates/creative-brief.md](../templates/creative-brief.md)）
- `02_visual_recipe.md` —— 视觉配方（[templates/visual-recipe.md](../templates/visual-recipe.md)）
- `03_generation_prompts.md` —— 可复制提示词（[templates/generation-prompts.md](../templates/generation-prompts.md)）
- `04_storyboard.md` —— 视频分镜（仅视频，[templates/video-storyboard.md](../templates/video-storyboard.md)）
- `05_quality_report.md` —— 质量检查与纠错（[templates/quality-report.md](../templates/quality-report.md)）
- `06_series_bible.md` —— 角色与系列一致性（仅系列，[templates/series-bible.md](../templates/series-bible.md)）
- 实际生成的图片/视频与缩略图；
- `README.md` 说明哪些已完成、哪些仍需外部执行。

## 三、用户面总结（保持简短）

1. 推荐概念；
2. 已产出什么；
3. 主要质量注意事项（若有）；
4. 实际文件/资产链接（环境支持时）。

## 四、模板使用约定

- 模板是起点，按需增删字段，不留空标题；
- 所有模板均不绑定具体生成模型，提示词正文只含可执行指令；
- 示例产物见 [../examples/example-fashion-brief.md](../examples/example-fashion-brief.md)。
