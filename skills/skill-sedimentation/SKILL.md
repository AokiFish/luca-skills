# skill-sedimentation

经验第一次做对、或第一次犯错，就写成 skill。不等纠正 2–3 次。

## 规则

1. 触发：真实工作出现重复模式，或同一失败模式第一次出现，就写 skill。旧口径「同一错误被纠正 2–3 次再升级」已废止——2026-11-15 展示区教训证明，等下去只会让同一个错再犯一遍：换装服装行 v45 平滑滚动做对了当时没写，v79/v83 轮播又瞎写了一遍瞬跳。再犯同类重复错误不可接受；防重复的唯一办法就是当时写。
2. 顺序：报 bug 时先修 bug，修好立刻写 skill。不许以写 skill 代替修 bug，也不许修完拖着不写。
3. 每个 skill 要短、要具体：规则 + 做法 + 验收 + 来源（日期 + 哪件事触发的）。不许空话，不许编造教训。
4. 存放：正本在 https://github.com/AokiFish/luca-skills，`skills/<name>/SKILL.md`，README 表格加一行，提交信息用英文；本地 ~/workspace/custom-skills/ 只留已安装副本。该仓 README 开头「视觉创作 Skill 集合」不用改。推送前确认 Muse GitHub App 已装在该仓，否则 403。
5. 登记：~/workspace/skills-base/LEDGER.md 记一行——名字、归属 Bot、来源（原创 / 改编自 pstack 的哪个 skill / 直接采用）、状态、日期。
6. 基底：Lauren Tan 的 pstack（cursor/plugins 仓库 pstack/ 目录，MIT，© Lauren Tan；backnotprop/pstack 只是镜像）。只读快照在 ~/workspace/skills-base/pstack/，永不在快照里直接改，更新靠重新同步。慢慢沉淀，不一次性搬空 61 个；新 skill 只在真实工作暴露重复模式或反复失败模式时写。
7. Eggbot 定期审计登记册：长期没被用过的采用项删掉；反复用顺手的原创项正式化。

## 使用铁律（Luca 2026-11-15 立，全局所有 Bot、所有空间）

有 skill 就先调 skill，不许自己乱搞；默认按学到的 skill 做，除非 Luca 让重新调整或修改。不许再犯重复的错误，不许让 Luca 重复同样的话。派活时 brief 必须点名适用的 skill，bot 做事前先读 skill。

## 验收

- Skill 文件有规则、做法、验收、带日期的来源四项；缺一项不算写完。
- 登记册有对应行；正本与本地副本内容一致。
- 登记后，技术栈总览空间（slug ji-shu-zhan-zong-lan）须同步新增卡片并更新总数与同步日期；批量写 skill 时该空间的更新是同一批工作的收尾，不是另起的任务。

## 来源

Luca 2026-11-08 定 skills foundation；2026-11-14 定存放位置；2026-11-15 18:40 纠正沉淀时机（第一次做对/犯错就写，不等 2–3 次；是所有经验，不只展示区平滑这一个）。见 ~/AGENTS.md「Skills foundation」「Skill 存放位置」与 ~/workspace/skills-base/LEDGER.md。
