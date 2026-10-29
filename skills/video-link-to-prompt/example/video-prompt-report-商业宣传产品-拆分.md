# 雅诗兰黛小棕瓶 30s TVC — 拆分生成方案（3×10s，适配 Muse AI）

> 配套文件：`video-prompt-report-雅诗兰黛TVC.md`（全片拆解）
> 适用工具：Muse AI（单次最长 10s，支持 text-to-video / image-to-video）
> 原则：**现有文件不动，本文件仅新增**。每段自洽可独立生成，并用"衔接锚点"保证三段拼接无缝。

---

## 0. 拆分逻辑（对齐镜头切点，不是硬切 10s）

| 段 | 物理时间 | 覆盖镜头 | 画面落点（衔接锚点） |
|---|---|---|---|
| 段 1 | 0–10s | 1→2→3→4 + 镜头5开头 | 她从棕色皮椅**起身、回头望窗**的第一刻 |
| 段 2 | 10–20s | 5→6→7→8 | 正面面部特写，眼神平静笃定（情绪顶点） |
| 段 3 | 20–30s | 9→10 | 产品英雄镜头收尾，光晕扫过瓶盖 |

> 切点选在镜头切换处（约 9.5s / 19.5s），**避开运动中硬切**，拼接更顺。
> 旁白分配：段1含 VO①全 + VO②开头；段2含 VO②收尾（"清醒不只属于白天"峰值）；段3含 VO③。

---

## 段 1（0–10s）：下班仪式 → 产品介入

**画面弧线**：合电脑（钩子）→ 滴管悬滴 → 侧脸上脸 → 金盖刻字 → 起身望窗起手

**中文 prompt**
> 高端护肤品广告前 10 秒，16:9，深夜都市高层。镜头1：大特写，女性手缓缓合上发蓝光的笔记本电脑，冷蓝调，城市 bokeh 虚化背景。镜头2：极特写微距，金色滴管悬于手背上方，一滴琥珀色精华将落未落，人脸虚化在背景。镜头3：短发知性女性（蓝灰无袖上衣）侧脸大特写，指尖把精华抹上颧骨，皮肤水光透亮，浅景深。镜头4：金色瓶盖与 ESTĒE LAUDER 刻字微距特写，深蓝背景。结尾：她从棕色皮椅起身、回头望向窗外夜景的第一刻。冷蓝与暖橙双色调，电影感光影，舒缓钢琴起。无字幕。

**English prompt**
> Premium skincare ad, first 10s, 16:9, late-night high-rise. Shot1: macro, a woman's hand slowly closes a glowing laptop, cool blue tone, city bokeh. Shot2: extreme close-up, a gold dropper hovers above the back of her hand, one drop of amber serum about to fall, face blurred behind. Shot3: profile close-up of a short-haired woman (slate-blue sleeveless top), fingertips press serum onto cheekbone, luminous skin, shallow DOF. Shot4: macro of gold cap with ESTĒE LAUDER engraving, deep-blue background. End: she rises from a brown leather chair and turns to glance at the night window for the first moment. Cool-blue vs warm-amber duotone, cinematic, soft piano intro. No subtitles.

**音频规划**：VO①"世界安静，夜晚才属于我，这一刻我留给自己"（0.8–3.5s） + VO②开头"一滴开启我的夜间…"（6.8s 起）。10–17s 的留白属于段2，**本段结尾音乐淡出留口子**。

**衔接锚点（给段2的首帧）**：`她从棕色皮椅起身、回头望向窗外` —— 这是段1最后一帧，也是段2第一帧，动作连续。

---

## 段 2（10–20s）：独处留白 → 情绪顶点

**画面弧线**：起身独步 → 闭眼再睁眼 → 玻璃幕墙空镜 → 正面特写

**中文 prompt**
> 高端护肤品广告中段 10 秒，16:9。接续：短发女性从棕色皮椅起身，中景跟拍，她缓步走过暖灯照亮的室内，先闭眼（呼吸、舒展）再睁眼，神情平静。插入深蓝色玻璃幕墙夜景空镜（规则窗格），全片最暗一拍。结尾：她面向镜头正面面部特写，眼神笃定，暖灯勾边——情绪顶点。冷暖双色调，浅景深，安静氛围，音乐极简留白（仅环境底噪）。无字幕。

**English prompt**
> Premium skincare ad, middle 10s, 16:9. Continuation: the short-haired woman rises from the brown leather chair, medium shot tracking, she walks slowly through a warmly lamp-lit interior, eyes closed (breathing, relaxing) then open, calm. Insert a dark-blue glass-tower night exterior (regular window grid), the darkest beat. End: a front facial close-up facing camera, assured gaze, warm rim light — emotional peak. Cool-warm duotone, shallow DOF, quiet ambience, minimal music (only ambient bed). No subtitles.

**音频规划**：前半 10–17s **纯音乐留白**（关键高级感来源，不要铺满）；17.5–19.5s VO②收尾"…清醒不只属于白天"达到人声峰值。段1尾音乐淡入此段。

**衔接锚点（给段3的首帧）**：`她正面面部特写、暖灯勾边` 之后直接切产品光晕——段3首帧用"金盖刻字 + 一道光晕刚扫入"承接。

---

## 段 3（20–30s）：产品英雄镜头收尾

**画面弧线**：金盖光晕 → 8 秒产品英雄镜头 → 缓缓收束

**中文 prompt**
> 高端护肤品广告结尾 10 秒，16:9。起手：金色瓶盖 ESTĒE LAUDER 刻字微距，一道镜头光晕扫过瓶盖。主体：棕色玻璃瓶配金色瓶盖的英雄镜头，"Advanced Night Repair" 标签清晰，夜景 bokeh 背景，镜头缓慢微移、光线流动至结束。冷蓝基底 + 暖金反光，奢华质感，电影感。结尾自然淡出。无字幕。

**English prompt**
> Premium skincare ad, final 10s, 16:9. Opening: macro of gold cap with ESTĒE LAUDER engraving, a lens flare sweeps across the cap. Body: hero shot of a brown glass bottle with gold cap, "Advanced Night Repair" label sharp, city bokeh background, slow camera drift and light play until the end. Cool-blue base with warm-gold reflections, luxurious texture, cinematic. Gentle fade-out. No subtitles.

**音频规划**：VO③"雅诗兰黛小棕瓶，让夜晚与自己重新同步"（19.5–27s），音乐在 27–30s 收束。段2尾的人声峰值平滑接入本段 VO。

---

## 怎么才能更好衔接（实操清单）

### A. 首选：首尾帧硬衔接（无缝核心）
Muse AI 支持 image-to-video。每段生成后，**把该段最后一帧导出**，作为下一段的"首帧/参考图"输入。
- 段1末帧 = 段2首帧（起身望窗）
- 段2末帧 = 段3首帧（正面特写 → 切产品光晕）

这是消除"跳帧感"最有效的手段，比纯文生视频连贯得多。

### B. 角色 / 产品锁定（一致性）
生成前各准备 1 张定妆参考图，每段都带同一张：
- 人物参考：短发、蓝灰无袖、冷调肤光（避免每段脸变）。
- 产品参考：小棕瓶金盖外观（避免瓶型/字位移）。

### C. 运动连续性
- 方向一致：段1→段2 都是"缓慢推进/跟拍"，不要段1慢推、段2突然横移。
- 速度一致：统一"舒缓"节奏，Muse 的运动强度参数三段设同一档。
- 景别过渡：段2结尾正面特写 → 段3起手微距金盖，是"特写→特写"平滑过渡，不要跳到大全景。

### D. 音视频分离（强烈建议）
1. 三段先生成**纯画面**（静音或仅环境底噪）。
2. 单独做一条 30s 统一配乐 + 统一 VO 配音（VO 三段由同一配音员、同一设备录，避免音色跳变）。
3. 后期把音频按 0–10 / 10–20 / 20–30 对齐贴回，再做 0.5s 交叉淡化。
4. **留白段（10–17s）务必保留静默**——别让 AI 把音乐铺满，那是高级感的来源。

### E. 色彩 LUT 统一
三段导出后用同一调色（冷蓝 + 暖橙双色温、轻微电影颗粒）。否则每段白平衡漂移会显廉价。

### F. 切点容错
每段生成时让画面在切点前后各留 0.3–0.5s 余量（如段1在第 9.5s 已出现"起身"，段2从 9.5s 同一动作接），剪辑时按实际最佳切点裁，而非死卡 10.000s。

---

## 交付与下一步
- 本目录新增：`video-prompt-report_拆分.md`（即本文件）
- 建议顺序：先生成**段1**（含钩子，定调最重）→ 段2 → 段3，每段都用上一段末帧做首帧。
- 若要投 9:16 竖屏信息流，需重构图（人物特写优先、产品居中），可再出一份竖屏拆分。
