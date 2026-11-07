# Skill 注册表与路由

> 注册表是“当前快照”，会随安装变化而过时。编排前若路由不确定，先跑 `scripts/list_skills.py` 扫描本地 Skill 根刷新。

## 一、内容生产链路

| Skill | 能力 | 典型输入 | 典型输出 |
|---|---|---|---|
| `visual-director` | 参考图/视频/一句话创意 → 可执行视觉方案 | 参考素材、brief | 视觉方案、生成提示词 |
| `doubao-creative-design` | 出图、海报、主视觉、编辑修图 | 设计需求 | 图片 |
| `doubao-creative-video` | 视频生成规划、文生/图生视频 | 脚本、参考图 | 视频 |
| `seedance-tvc-director` | 品牌 TVC 创意与导演执行单 | 品牌 brief | 方案、提示词、分镜 |
| `video-link-to-prompt` | 逐镜头拆解视频 → 生成提示词/分镜表 | 视频链接/文件 | 提示词、分镜表 |
| `video-downloader` / `video-dl` | 下载各平台视频到本地 | 视频链接 | 本地 mp4 |
| `video-mix` | 多段短视频拼接 + 配乐 | 视频目录 | 成片 |
| `video-music-extract` | 视频抽音轨（可去人声） | 视频链接 | mp3 |
| `music-instrument-analysis` | 音乐乐器识别与配器分析 | 音频 | 分析报告 |
| `image-reference-to-prompt` | 参考图反推提示词 | 图片 | 提示词 |
| `github-weekly` | GitHub 周榜解说短视频全流程 | 周榜数据 | 成片、封面、字幕 |
| `cover-studio` | 12套小红书/短视频封面模板 → 竖版或横版封面（主角：丸子头女生） | 标题文案、模板号、可选本人照片 | `cover.png` |
| `cat-cover-studio` | 同上，主角固定为乳色英短猫（粉蝴蝶结+金铃铛） | 标题文案、模板号、猫咪姿态偏好 | `cover-cat.png` |
| `byted-mediakit-*` | 专业媒体处理（转码、抽帧、ASR、字幕、擦除、增强） | 媒体文件 | 处理结果 |

## 二、文案与发布链路

| Skill | 能力 | 典型输入 | 典型输出 |
|---|---|---|---|
| `video-publish-pack` | 一条视频 → 多平台标题/描述/标签/双语字幕（文案适配层） | 视频、剧情、目标平台 | `content-pack.json`、字幕、对照表 |
| `sau-publish` | 调用 `sau` CLI 真正发布 + 登录 + 核验（发布执行层） | `content-pack.json`、账号、视频 | 平台作品、核验截图 |

**固定配对**：先 `video-publish-pack` 产出内容包，再 `sau-publish` 执行发布。前者不改环境，后者不改文案。

## 三、交付与文档链路

| Skill | 能力 |
|---|---|
| `lark-doc` | 飞书/豆包在线文档创建与编辑 |
| `word` / `pdf` / `sheet` / `ppt` | 本地 Office 文件生成与编辑 |
| `html` | 独立 HTML 页面、深度研究报告 |
| `doubao-visualization` | 图表、图解、可视化 |
| `verifier-hub` / `artifact-preview` | 交付前确定性校验 / 渲染预览 |
| `doubao-book-writer` | 长文档、白皮书、手册 |

## 四、路由规则（按目标选，不按文件后缀选）

| 用户目标关键词 | 首选 Skill |
|---|---|
| 做图 / 海报 / 主视觉 / 修图 / 元素替换 | `doubao-creative-design` |
| 做视频 / 文生视频 / 图生视频 / 广告片 | `doubao-creative-video` |
| 视频转码 / 抽帧 / 识别字幕 / 去水印 / 擦字幕 | `byted-mediakit-*` |
| 起标题 / 写描述 / 配标签 / 多平台文案 / 字幕 | `video-publish-pack` |
| 做封面 / 视频封面 / 小红书封面 / thumbnail / 换标题做封面 | `cover-studio`（普通内容）或 `cat-cover-studio`（猫咪IP/萌宠） |
| 发布 / 上传 / 登录 / 发抖音 / 发 B 站 | `sau-publish` |
| 多个步骤按流程走 | `task-conductor`（本 Skill） |
| 表格 / Excel / CSV | `sheet` |
| 幻灯片 | `ppt` |
| Word / 公文 | `word` |
| 飞书文档 | `lark-doc` |

## 五、边界提醒

- 同一能力有多个 Skill 时，选**职责最窄**的那个，不要用大而全的替代专用能力。
- `video-publish-pack` 只产文案不发布；`sau-publish` 只发布不写文案。混用会破坏职责边界。
- `sau-publish` 不支持的平台（TikTok 无 CLI 等）要在计划里显式标注“需浏览器版/人工”。
