# Host Agent Visual Analysis Instructions

You are given `analysis_bundle.json` and timestamped keyframes/contact sheet. Use only images you can actually inspect.

1. Read the bundle for duration, frame timestamps, sampling interval, dimensions and audio availability.
2. Inspect the contact sheet for the sequence; inspect individual frames around changes or uncertain actions.
3. Refer to frames by filename and timestamp. Do not invent unseen intermediate action.
4. Label claims as `observed`, `inferred`, or `unknown`.
5. If sampling is too sparse to establish an action, say so and recommend a smaller interval.
6. Do not infer exact camera gear, aperture, original prompt, seed, or hidden generation settings.
7. Produce structured notes: premise/hook/payoff; ordered beats and frame timestamps; possible shot boundaries with confidence; subject/environment/props/continuity; framing/movement; lighting/color; audio only if available; transferable creative methods; unknowns and needed evidence.
8. Follow `SKILL.md` for the final breakdown and prompt.
