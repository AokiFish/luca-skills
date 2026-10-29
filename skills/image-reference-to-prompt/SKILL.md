---
name: image-reference-to-prompt
description: Analyze an uploaded reference image and turn its visible visual structure into a precise, reusable image-generation prompt. Use whenever a user uploads an image and asks to reverse-engineer it, recreate it, write a similar prompt, preserve composition, or adapt it for an image model.
---

# Image Reference → Prompt Skill

## Mission

Turn the *specific visible image* into an actionable generation prompt that preserves what makes it recognizable. Do not produce a generic description, an art critique, or a pile of aesthetic adjectives.

**Primary workflow:** inspect the actual image → map composition and relationships → identify the few details that carry likeness → write a compact prompt → audit it against the image.

This skill uses the host agent's native image understanding. Do not require an API key, ask the user to install Python, or pretend that a script can semantically inspect an image. If the current environment cannot view the uploaded image, say so clearly and ask the user to attach it in a vision-capable interface.

## Default behavior

- If the user uploads an image and says only “分析一下 / 反推提示词 / 做成类似的图”, proceed without asking questions.
- Output in the user's language by default. For image-generation prompts, English is acceptable when useful for the target model; include Chinese only if requested or if the target model performs better with it.
- If no target platform is specified, produce a **platform-neutral prompt** first. Do not assume Midjourney, Stable Diffusion, Flux, or any Chinese platform.
- Do not claim exact camera/lens/model settings from pixels alone. Label such values as optional creative choices, not observed facts.
- Preserve the image's intent and key layout, but do not infer hidden biography, identity, ethnicity, brand, location, or backstory unless visible or supplied by the user.
- If multiple images are supplied, determine whether they are references for the same output or separate tasks. State the role of each image only when it affects the prompt.

## Step-by-step procedure

### 1. Establish the image's visual contract

Inspect the whole image first, then inspect important regions. Record only visible evidence.

Create a compact internal ledger with three labels:
- **Observed:** directly visible (e.g. face sits in the right third; foreground ornament is blurred).
- **Inferred:** likely interpretation but not certain (e.g. soft backlight may come from a window).
- **Unknown:** cannot reliably tell (e.g. exact lens, camera model, real location).

Never turn an inference into a factual claim. Do not show a long ledger unless it helps the user; use it to avoid hallucination.

### 2. Map composition with normalized coordinates

Treat the canvas as a coordinate plane: left-to-right x = 0–100%, top-to-bottom y = 0–100%. Estimate regions rather than inventing pixel-perfect coordinates.

Describe:
- aspect ratio and crop (portrait / landscape / square; tight close-up, head-and-shoulders, half-body, full body, wide shot)
- subject placement and scale (center, left/right third, upper/lower half; approximate proportion of frame)
- head/body orientation separately from eye direction
- where hands, props, jewelry, hair, text, or key objects sit
- what is cropped by each edge
- negative space and the visual path from foreground to subject to background

Coordinates are a communication aid, not a promise of exact reconstruction. Use ranges (e.g. x=62–98%, y=8–92%) only for high-impact objects.

### 3. Build a relationship map (the most important step)

For each major element, identify its relationship to other elements:
- **position:** left of / above / behind / crossing / touching / partly outside frame
- **scale:** dominant / secondary / tiny accent
- **occlusion:** what covers what
- **depth:** foreground blur / sharp subject plane / soft background
- **focus:** which feature is sharpest; which regions lose detail
- **direction:** face turned one way, eyes looking another; light comes from a stated side
- **gesture:** head tilt, shoulder angle, hand placement, line of action
- **contrast:** bright subject against dark background, warm light against cool shadows, etc.

Weak: “ornate jewelry, beautiful woman, cinematic lighting.”
Useful: “A large gold-and-pearl hair ornament enters from the left foreground and is heavily out of focus; the sharply focused face occupies the right third, with small blue gems arranged along the temple.”

Prioritize relationships that would cause a visibly different result if changed.

### 4. Rank the visual anchors

Choose **3–5 must-preserve anchors**. They should be specific enough to distinguish this image from thousands of similar images. Typical anchors:
1. composition/crop and subject placement
2. face direction, expression, and gaze
3. signature accessory / clothing silhouette / prop placement
4. lighting direction and depth-of-field structure
5. distinctive palette or background geometry

Do not waste an anchor on generic terms such as “high quality,” “beautiful,” “detailed,” or “cinematic.”

### 5. Analyze lighting, color, texture, and rendering

Describe observable properties:
- light source direction, softness, intensity, backlight/rim light, shadow behavior
- palette hierarchy: dominant hue, secondary hue, small accent colors; warm/cool balance
- surface qualities: skin texture, metal/pearl/gem sheen, fabric weave, hair flyaways
- focus falloff, grain, bloom, haze, motion blur, edge sharpness
- realism level: photoreal, editorial photograph, painterly, illustration, 3D, anime, mixed media

Use HEX values only if color precision genuinely matters; otherwise use plain language. Never add fake numerical precision for decoration.

### 6. Convert analysis into generation instructions

Write the prompt in this order:
1. **Subject + image type**
2. **Framing and placement**
3. **Pose / face orientation / gaze / expression**
4. **Distinctive objects and their exact relationships**
5. **Lighting and depth of field**
6. **Color and material rendering**
7. **Background and mood**
8. **Quality controls / exclusions**

Make the most important constraints early. Use short, concrete clauses. Avoid adjective stacking and redundant style tags. A prompt is not a prose essay.

Use exclusions only to prevent plausible failures visible in the reference or requested by the user. Do not automatically append giant negative-prompt lists.

### 7. Run a contradiction audit

Before answering, check:
- Does the prompt put the subject in the same part of the frame?
- Does it preserve crop boundaries and subject scale?
- Are head direction and gaze described separately?
- Are signature objects on the correct side and in the correct depth plane?
- Does the light come from the correct direction?
- Is the sharp/blurred hierarchy consistent?
- Are colors prioritized rather than listed indiscriminately?
- Did the prompt invent unsupported details?
- Is it concise enough that the image model can follow it?

If any of the top three anchors are missing or contradictory, revise before responding.

## Default output format

Use this output unless the user asks for a different format:

### 1. 这张图的关键视觉结构
- **构图：** one or two specific sentences, including crop and subject placement.
- **视觉锚点：** 3–5 ranked items.
- **空间关系：** foreground / subject plane / background, plus critical object relationships.
- **光色与质感：** lighting direction, palette hierarchy, material and focus behavior.
- **不确定项：** only if relevant; do not overdo caveats.

### 2. 可直接使用的生成提示词
Provide one complete prompt in a clean copyable block. The prompt should stand on its own and must not refer to “the uploaded image” because the image model may not receive that reference.

### 3. 负面约束
Only if needed. Keep it short and specific. If the target platform has no dedicated negative-prompt field, phrase exclusions naturally in the main prompt.

### 4. 复现检查点
Give three short checks the user can compare against the generated result, such as subject placement, accessory location, and focus hierarchy.

Do not force all four sections for simple requests. If the user only wants the prompt, return the prompt first and keep analysis brief.

## Platform adaptation

If the user names a platform, adapt syntax and settings only when you have reliable knowledge of that platform. Keep the visual description intact; platform syntax is a wrapper, not the analysis.

- **Unknown / unspecified:** platform-neutral natural-language prompt, no model flags.
- **Midjourney:** add supported aspect-ratio or version parameters only when known and relevant; do not invent flags.
- **Stable Diffusion / SDXL / Flux:** separate positive and negative prompts only if the chosen UI/model supports them. Do not assume all models interpret weights the same way.
- **Chinese image-generation websites:** use clear natural-language instructions and avoid unsupported parameter syntax.
- **If user asks for multiple platforms:** reuse the same visual core, then create separate concise platform variants. Do not imply prompts are guaranteed identical across models.

## Iteration mode

If the user shares a generated result and says it does not match:
1. Compare the result with the original reference, not with your previous prose alone.
2. Identify the **three largest visual mismatches** (e.g. composition, accessory position, light direction).
3. Change only the prompt clauses tied to those mismatches; do not rewrite everything randomly.
4. Return a revised prompt and a brief “changed because” list.
5. If the output repeatedly fails at precise placement, explain that text prompts cannot guarantee pixel-level layout and suggest image-reference, inpainting, regional prompting, or pose/layout controls if the target tool supports them.

## Quality bar

A good result must be **image-specific, spatially grounded, relational, concise, and directly usable**.

Reject these failure modes:
- generic prompt templates with only subject/style swapped
- unsupported claims about camera, lens, film stock, exact lighting equipment, or model
- lists of attractive adjectives without geometry
- mixing every visible color or object with equal importance
- adding narrative elements not present in the image
- bloated negative prompts
- claiming the output will reproduce the reference exactly
- asking the user to configure an API key as a prerequisite

## If image understanding is limited

Do not fake details. Say which parts are unclear and produce a best-effort prompt from visible evidence. If the image is inaccessible or cannot be visually inspected in the current environment, state that limitation and ask for the image to be attached in a supported way. Do not substitute a generic prompt and call it reverse engineering.
