# Host Agent Visual Analysis Instructions

You are given `analysis_bundle.json`, timestamped keyframes, and the `sheets/` evidence package (paginated `sheet_XX.jpg`, `_cuts.txt` when `--scene-cuts` was used, and a blank `动作模板.md`). Use only images you can actually inspect.

1. Read the bundle for duration, frame timestamps, sampling mode, scene-cut count, average beats/second, dimensions and audio availability.
2. Inspect the **paginated contact sheets** `sheets/sheet_XX.jpg` for the sequence, page by page; inspect individual frames under `frames/` around changes or uncertain actions. If scene-cut frames exist, read them **in order** — each is the start of a new shot/beat.
3. Refer to frames by filename and timestamp. Do not invent unseen intermediate action.
4. Label claims as `observed`, `inferred`, or `unknown`.
5. If sampling is too sparse to establish an action, say so and recommend a smaller interval or `--scene-cuts`.
6. Do not infer exact camera gear, aperture, original prompt, seed, or hidden generation settings.
7. **Fill `sheets/动作模板.md`** as you read: for each `sheet_XX` page, write the ordered action beats into its table. This file is the single source of truth for the later shot breakdown.

For every shot/unit, extract and record these fields (they are the core deliverable — without them the breakdown cannot be reused for a new character):
- **景别 (shot size):** 大远景 / 远景 / 全景 / 中景 / 中近景 / 近景 / 特写 / 大特写.
- **机位 (angle):** 平视 / 仰拍 / 俯拍 / 顶视.
- **运动 (camera movement):** 固定 / 推 / 拉 / 摇 / 移 / 跟 / 升降 / 环绕 / 手持 / 航拍 / 俯瞰.
- **动作节拍 (action beats):** ordered ① ② ③ visible verbs with start→middle→end. Ground each in a frame; do not fabricate. Count beats and compare to the bundle's `avg_beats_per_second` — a 10s unit at ~2.3s/beat should carry 3–5 beats.
- **声音 (sound):** for dialogue-free video, log non-verbal cues (grunts, gasps, ambient, stingers); for spoken video, log dialogue + ambience.
- **段色调 (segment color tone):** the dominant palette keyword for that segment.
- **结尾定格 (end-frame anchor):** describe the last frame so the next unit can begin there with zero jump.

7. Build a **role map** of character placeholders (`[主角1]` etc.) → source roles → reference image files; describe only each character's actions/expressions, never their looks (looks come from `image-reference-to-prompt`).
8. Write one **verbatim style sentence** (CN + EN) and paste it into every unit.
9. Produce structured notes: premise/hook/payoff; ordered beats and frame timestamps; possible shot boundaries with confidence; subject/environment/props/continuity; framing/movement; lighting/color; audio only if available; transferable creative methods; unknowns and needed evidence.
10. Follow `SKILL.md` for the final breakdown and prompt.
