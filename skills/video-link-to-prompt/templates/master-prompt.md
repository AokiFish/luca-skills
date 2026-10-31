# Reusable Video Master Prompt

Replace bracketed fields with concrete values before generation. Characters are **placeholders** (`[主角1]` / `[主角2]` / `[反派3]`) — their looks come from reference images, not from this text.

## Creative brief
- **Duration / aspect ratio:** [TARGET DURATION] / [ASPECT RATIO]
- **Core idea:** [ONE-SENTENCE PREMISE]
- **Opening hook:** [FIRST VISUAL EVENT]
- **Main subject / setting:** [MAIN SUBJECT] / [SETTING]
- **Goal / obstacle:** [GOAL] / [OBSTACLE]
- **Escalation:** [HOW THE SITUATION DEVELOPS]
- **Payoff:** [PAYOFF / TWIST / EMOTIONAL BEAT]
- **Visual identity:** [VISUAL STYLE], [COLOR PALETTE], [LIGHTING]
- **Sound:** [SOUND DESIGN OR MUSIC DIRECTION]

## Unified style sentence (paste verbatim into every unit; CN + EN)
- CN: [STYLE SENTENCE — e.g. 皮克斯风格 3D 动画电影质感，柔和电影级光照，浅景深，16:9 画幅，全程同一渲染管线]
- EN: [STYLE SENTENCE — e.g. Pixar-style 3D animated film look, soft cinematic lighting, shallow depth of field, 16:9, consistent render style throughout]

## Role map (placeholder ↔ source role ↔ reference image)
- `[主角1]` ↔ [SOURCE ROLE] ↔ [image file]
- `[主角2]` ↔ [SOURCE ROLE] ↔ [image file]
- `[反派3]` ↔ [SOURCE ROLE] ↔ [image file]

## Rhythm constraint
- Average beat interval: [BEAT INTERVAL]s (cut count ÷ duration). Each generation unit of [UNIT DURATION]s must hold **[N] beats**, not one slow action.

## Shot plan (one block per generation unit)
**Unit [N] | [TIME RANGE] | 景别:[SHOT SIZE] | 机位:[ANGLE] | 运动:[MOVEMENT] | 段色调:[TONE]**
- 动作节拍 ① [BEAT 1 start→middle→end] ② [BEAT 2] ③ [BEAT 3] …
- 声音：[NON-VERBAL CUES / AMBIENCE / MUSIC]
- 中文：> [STYLE SENTENCE] [段色调]。[剧情：[BEATS AS ACTION SENTENCE]]。[景别/运动描述]。结尾定格：[END FRAME]。
- EN: > [STYLE SENTENCE EN] [TONE]. [Plot: BEATS]. [SIZE/MOVEMENT]. End frame: [END FRAME].
- 结尾定格（下一单元首帧）：[END FRAME DESCRIPTION]

Adjust the unit count to the duration; do not force a fixed number if fewer or more are appropriate.

## Fixed quality rules
- One readable primary action per beat; clear start, middle and end for important movement.
- Camera movement supports the action and does not compete with it.
- Explicit shot size + angle + movement on every unit.
- Maintain subject identity, wardrobe, props, environment and screen direction.
- Keep lighting/color coherent within a segment; switch tone only at segment boundaries.
- Make the hook legible immediately and give the payoff enough time.
- Characters appear only as placeholders; describe action/expression, never looks.
- End-frame anchor stated on every unit so units chain with zero jump.
- Avoid contradictory actions, excessive adjectives and unrelated effects.
- [REFERENCE-DERIVED TRANSFERABLE RULES]

## Replaceable variables
[MAIN SUBJECT], [SETTING], [GOAL], [OBSTACLE], [KEY PROP], [ESCALATION], [PAYOFF], [VISUAL STYLE], [COLOR PALETTE], [SOUND DESIGN], [TARGET DURATION], [ASPECT RATIO], [TARGET MODEL], and the per-unit `[剧情：…]` block.

## Model settings (separate from prompt)
- Model/version: [MODEL]
- Duration: [SUPPORTED DURATION]
- Aspect ratio/resolution: [SUPPORTED OPTIONS]
- Reference inputs: [SUPPORTED INPUTS]
- Audio: [SUPPORTED / NOT SUPPORTED / UNKNOWN]
- Negative prompt/other controls: [ONLY IF SUPPORTED]
