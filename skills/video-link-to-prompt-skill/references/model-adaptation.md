# Cross-Model Adaptation Rules

## Principle

Keep three layers separate:

1. **Creative brief** — story, subject, action, mood, visual identity.
2. **Generation prompt** — natural-language instructions that the selected model understands.
3. **Model controls** — duration, aspect ratio, resolution, reference inputs, audio toggle, seed, negative prompt, and other UI/API fields.

Never assume that a control exists just because another model offers it.

## Model-agnostic prompt structure

1. Subject and scene
2. Primary action and temporal progression
3. Camera framing and movement
4. Lighting, color, and visual texture
5. Environment interaction and physical detail
6. Audio/dialogue, only when supported or intended for post-production
7. Continuity and exclusions, phrased positively where possible

## Adaptation checklist

- Confirm exact model and version.
- Check official, current documentation for duration, aspect ratio, resolution, audio, reference-image/video inputs, multi-shot behavior, and negative-prompt support.
- Remove unsupported controls from the final request.
- Keep UI/API parameters outside the natural-language prompt when the platform has dedicated fields.
- If using image-to-video, describe how the existing image should move; do not needlessly re-describe every static visual detail.
- If using start/end frames, define the transition and the final state, not just the two images independently.
- For character consistency, use reference inputs when supported and describe stable identity markers.
- For longer videos, split into coherent shots or clips if the model has limited duration/control; specify matching start/end states across clips.
- Do not guarantee exact compliance. Video generation is probabilistic; recommend targeted iterations.

## Model notes

These are adaptation heuristics, not a substitute for checking current official documentation:

- **Google Veo:** use clear scene/action/camera/light/sound descriptions; verify current model and audio capabilities.
- **OpenAI Sora:** describe temporal progression and shot intent clearly; confirm current availability, model version, and API controls.
- **Kling:** write concise Chinese or English instructions around subject, movement, scene, camera, and lighting; verify the current interface's duration/aspect-ratio/reference controls.
- **Runway:** prioritize clear subject motion and camera motion; use current model guidance, not retired model-specific assumptions.
- **Other models:** retain the creative brief and translate only the syntax and supported controls.

## Avoid
- Long strings of unrelated style adjectives.
- Multiple incompatible camera movements in one shot.
- Describing every possible sound if no audio is supported.
- Mixing technical metadata into prose when a dedicated control exists.
- Treating “8K”, lens names, or camera brands as magic quality switches.
