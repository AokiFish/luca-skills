---
name: image-reverse-engineering
description: Reverse-engineer a supplied reference image into a high-fidelity, platform-aware image-generation prompt. Use when a user asks to analyze, recreate, imitate the visual structure of, or derive a prompt from an image.
---

# Image Reverse Engineering Skill — v3

## Mission
Do not merely describe what is in an image. Convert the image into **controllable visual constraints** that help another image model reproduce its visual identity.

Core unit of analysis:
**visual element + approximate location + state/appearance + relationship to other elements + importance + confidence**.

Example:
- Weak: "jewelry on the left."
- Strong: "large dangling jewelry occupies the left third, sits between camera and face, is closer to the lens than the face, and remains softly out of focus; it frames but does not cover the cheek."

## Capability architecture
1. **Image access**: use the host agent's image attachment/vision capability. If the image cannot actually be accessed, ask for a supported attachment or path. Never pretend to have inspected it.
2. **Deterministic inspection**: optionally run `scripts/analyze_image.py` for dimensions, aspect ratio, color estimates, luminance, contrast, edge strength and approximate region statistics. These are measurements, not semantic understanding.
3. **Semantic vision**: use a vision-capable model for objects, pose, gaze, spatial relationships, materials, light, and composition.
4. **Prompt compiler**: translate the analysis into concise, ordered, model-friendly instructions.
5. **Validation**: check contradictions, uncertainty, over-specification, and likely model failure modes.

## Mandatory workflow

### Phase 1 — Establish the frame
Record:
- image dimensions and aspect ratio (measure if file is available);
- orientation and crop type (extreme close-up, close-up, medium, full-body, wide);
- whether the image is one continuous scene, a collage, a multi-panel layout, or a screenshot;
- number of primary subjects and any text/logo that must be retained or excluded.

Do not assume the image is 16:9 based on appearance alone when measurements are available.

### Phase 2 — Build a spatial map
Use approximate normalized coordinates from 0% to 100% when the placement materially affects similarity. Avoid fake precision: use ranges unless a boundary can be estimated confidently.

Record:
- primary subject center (x%, y%);
- subject size (e.g. face height as % of frame height);
- crop boundaries (hair/top of head/chin/shoulders relative to frame);
- left/center/right visual zones;
- foreground / subject plane / background;
- sharp vs soft regions;
- negative space and bright/dark masses.

Use coordinates as **approximate anchors**, not as claims of exact pixel segmentation. If the vision model is uncertain, say "roughly" or use a broad range.

### Phase 3 — Describe relationships, not just objects
For every important element, describe relevant relationships:
- in front of / behind / beside / overlapping / framing / touching / separated from;
- closer to camera / same plane / farther away;
- gaze direction versus head direction;
- light source direction versus the highlights it produces;
- color contrast and material contrast;
- subject-to-frame and subject-to-background relationships.

Only include relationships that matter for recreating the reference.

### Phase 4 — Extract a visual fingerprint
Rank 3–5 **must-preserve anchors**, then 3–7 secondary traits. Typical anchors:
1. composition and crop;
2. silhouette / pose / gaze;
3. foreground-background layering;
4. light direction and exposure;
5. palette and material contrast;
6. distinctive ornament / clothing / graphic motif.

Do not automatically choose the subject category as the main anchor; the same "woman in costume" can yield radically different images.

### Phase 5 — Evidence and confidence
Separate:
- **Observed**: visibly supported details or measured properties.
- **Inferred**: plausible but uncertain interpretations, with confidence high/medium/low.
- **Unknown**: exact generator, model, seed, source prompt, lens/camera unless verified by provenance metadata.

Do not state a historical dynasty, lens, focal length, lighting equipment, or generation platform as fact unless the image or supplied context supports it. Style labels can be used as visual direction, not provenance claims.

### Phase 6 — Prompt compilation
Build the prompt in this order, changing the order only when the target platform benefits:
1. output type, aspect ratio, single scene / subject count;
2. shot scale, crop, subject placement, viewpoint;
3. pose, head orientation, gaze direction, expression;
4. foreground / midground / background relationships;
5. signature clothing, accessories, textures and exact placements;
6. light direction, fill, contrast, highlight behavior;
7. palette and color hierarchy;
8. medium, realism, depth of field, finish;
9. must-not-change constraints and output exclusions.

Make the prompt **specific, not merely long**. Prefer a small number of precise spatial and relational constraints over piles of generic quality words.

### Phase 7 — Contradiction and feasibility audit
Check at least:
- head direction versus gaze direction;
- face placement versus crop;
- foreground object sharpness versus depth of field;
- bright backlight versus face exposure;
- number of subjects and whether a continuous scene is requested;
- costume detail versus crop (do not invent full outfits outside frame);
- "soft light" versus "hard shadows";
- positive prompt versus negative constraints;
- bilingual versions for meaning conflicts.

If a detail is likely too brittle for a model (e.g. exact pupil position), convert it to a more robust visual instruction (e.g. "eyes glance strongly toward frame left while the head remains nearly facing camera").

### Phase 8 — Compile variants
Default: one strong primary prompt. Do not automatically produce many variants.
If the user names a platform, adapt to its conventions. If no platform is named, keep the prompt platform-neutral and avoid invented syntax.
If useful, include:
- **Faithful version**: preserve reference geometry and lighting.
- **Flexible version**: preserve the visual fingerprint but allow minor variation.
Do not duplicate the entire prompt in two languages unless the user asks; if bilingual output is requested, keep both versions semantically aligned.

## Required output contract
### A. Visual fingerprint
- 3–5 must-preserve anchors, ranked.
- Secondary traits.

### B. Spatial and relational map
A compact table or bullets with approximate coordinates, crop, depth plane, sharpness, and relationships where relevant.

### C. Evidence ledger
- Observed
- Inferred with confidence
- Unknown / unrecoverable

### D. Copy-ready prompt
A single coherent prompt, ordered from global structure to local detail. Use natural language and avoid redundant adjective piles.

### E. Drift-prevention constraints
Only constraints that directly prevent likely errors. Avoid a generic mega-list.

### F. Quality audit
Report contradictions found and how they were resolved. If no contradiction is found, state that briefly.

## Technical script
Optional:
```bash
python scripts/analyze_image.py IMAGE_PATH --out report.json
```
For semantic vision through an OpenAI-compatible endpoint:
```bash
export VISION_API_KEY="..."
export VISION_BASE_URL="https://api.openai.com/v1"
export VISION_MODEL="vision-capable-model"
python scripts/analyze_image.py IMAGE_PATH --vision --out report.json
```
Check the endpoint's image-input format and privacy policy. Some providers may not support data URLs or the same chat-completions schema.

## Cross-agent portability
- This package is the portable core, not a universal installer.
- Each host agent must be able to access the image and either provide native vision or call a configured vision endpoint.
- If Python execution is unavailable, the agent can still follow the workflow using its own vision capability.
- If neither image access nor a vision model is available, semantic reverse-engineering is not possible; ask for a supported connection.
- Do not bind the core workflow to proprietary SDKs. Host-specific adapters may be added separately.

## Reliability
- Never infer the exact original prompt, model, seed, or generator from pixels alone.
- Never present approximate coordinates as exact measurements unless computed from image segmentation or manual pixel inspection.
- Avoid identity claims about real people and sensitive trait inference.
- The image-generation prompt is a best-effort control specification, not a guarantee of pixel-identical reproduction.
