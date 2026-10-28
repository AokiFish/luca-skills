---
name: video-link-to-prompt
description: Analyze a user-provided video link or uploaded video, break it down into a grounded shot-by-shot creative analysis, and produce reusable cross-model video-generation prompts, storyboard tables, and model-specific settings. Use when the user asks to dissect, reverse-engineer, learn from, or create a prompt based on a reference video.
---

# Video Link → Shot Breakdown → Reusable Video Prompt

## Purpose

Turn a reference video into a practical creative blueprint, then produce an original video-generation prompt that can be adapted to Veo, Sora, Kling, Runway, and other video models.

The goal is not merely to describe what appears in the video. Identify the creative mechanism: hook, narrative progression, subject behavior, camera language, lighting, rhythm, sound, transitions, and continuity. Separate reusable techniques from reference-specific content.

## Trigger conditions

Use this skill when the user:
- provides a video URL and asks for analysis, breakdown, prompt extraction, or recreation;
- asks to turn a reference video into a prompt, storyboard, or production workflow;
- wants a reusable template that works across video models.

If the user only asks a simple question about a video, answer that question without forcing the full workflow.

## Operating principles

1. **Ground every observation.** Do not claim to have watched, heard, or extracted a video unless the actual video content was accessible. A URL alone is not proof that its media was read.
2. **Report access limitations early.** Try the available browser/web tools when appropriate. If the page is blocked, login-gated, region-limited, or only exposes metadata, say exactly what was and was not accessible. Ask for an uploaded video, a downloadable file, or key frames when needed.
3. **Separate evidence from inference.** Label important details as:
   - Observed: directly visible/audible in the accessible media.
   - Inferred: plausible interpretation, not directly confirmed.
   - Unknown: cannot be determined from the available material.
4. **Do not invent original prompts or production metadata.** A final video does not reliably reveal its original prompt, camera model, lens, aperture, model version, seed, or generation settings.
5. **Learn from, do not blindly clone.** Identify the reference's transferable creative techniques. When asked to create a new video, preserve the requested high-level method while changing the subject, story, setting, and other requested elements.
6. **Keep prompts economical.** Prefer clear, observable actions and coherent shot instructions over piles of adjectives. Avoid contradictory camera movements or multiple unrelated actions in one shot.
7. **Cross-model by design.** Keep creative intent separate from model-specific syntax and UI/API parameters. Never assume every model supports audio, negative prompts, reference images, multi-shot generation, or the same duration/aspect-ratio controls.
8. **Respect user priorities.** Ask one concise clarifying question only when an essential detail blocks progress. Otherwise use sensible defaults and clearly label them.
9. **Usability first.** Make outputs ready to use. Keep variable fields obvious, minimize unnecessary theory, and explain only decisions that materially affect the result.

## Workflow

### Step 1 — Intake and access check

Extract:
- video URL or uploaded asset;
- user's intended task: analyze, learn style, create a new video, or closely reproduce the structure;
- target model, if supplied;
- desired duration, aspect ratio, platform, and output format, if supplied.

If unspecified, default to:
- goal: analyze the reference and create an original adaptable prompt;
- duration: use the reference duration if known, otherwise leave as `[TARGET DURATION]`;
- aspect ratio: `[ASPECT RATIO]`;
- model: model-agnostic master prompt, followed by optional model-specific adaptation.

Attempt to access the media using available tools. Do not claim successful access just because a page title or thumbnail loaded.

### Step 2 — Evidence inventory

Record which sources are available:
- full video and audio;
- video only;
- audio only;
- captions/transcript;
- thumbnails or selected frames;
- page metadata only.

If a video cannot be played or downloaded, stop short of shot-specific claims. Give the user a clear fallback: upload the clip, provide a direct media link, or share key frames plus any dialogue/transcript.

### Step 3 — Analyze the reference

Analyze these layers where evidence permits:

1. **Creative premise** — one-sentence idea, audience, hook, emotional promise, memorable payoff.
2. **Narrative structure** — opening, development, escalation, reveal/turn, ending. Do not force a twist if none exists.
3. **Visual system** — subject, environment, props, costume, texture, composition, palette.
4. **Cinematography** — shot size, angle, framing, camera movement, focus/depth of field, camera-to-subject relationship.
5. **Action and timing** — visible action verbs, starting state, intermediate movement, ending state, pace, pauses, physical/environmental response.
6. **Lighting and color** — apparent direction, softness, contrast, exposure, color relationships. Do not assert exact equipment or numeric settings without evidence.
7. **Sound** — dialogue, ambience, foley, music, sync points, silence, perceived mix. If audio is inaccessible, mark unknown.
8. **Editing and continuity** — cut points, transitions, motion direction, eyelines, screen direction, recurring elements, continuity risks.
9. **Reusable technique** — explain why a design choice may work and how to transfer it to another subject.
10. **Improvement opportunities** — identify plausible improvements separately from observations.

### Step 4 — Build a shot table

For each shot, include only fields supported by evidence:
- shot number and approximate timecode;
- shot size and angle;
- subject and scene;
- primary action;
- camera movement;
- lighting/color;
- sound/dialogue;
- transition or continuity note;
- confidence/evidence note if uncertainty matters.

Use approximate timecodes if exact frame timing is unavailable. Mark them as approximate.

### Step 5 — Extract reusable design rules

Summarize:
- what should stay fixed across new creations (quality rules, continuity rules, chosen aesthetic identity);
- what should change (subject, setting, actions, story, props, dialogue, palette when appropriate);
- what must be model-specific (duration, resolution, aspect ratio, reference-frame inputs, audio support, negative prompt support, shot syntax).

Do not copy incidental reference details into the fixed rules.

### Step 6 — Generate the master prompt

Use the template in `templates/master-prompt.md`. Fill all known fields. Replace unresolved fields with clear placeholders such as `[DESCRIBE THE SCENE]`. Do not leave placeholders in a purported final, ready-to-run prompt unless the user explicitly requested a template.

Write observable, temporally coherent actions. For multi-shot work, describe each shot separately and state how continuity is maintained. For single-shot work, avoid adding unnecessary cuts.

### Step 7 — Adapt to the target model

If a target model is specified:
- consult current official documentation when access to web research is available and the behavior may have changed;
- separate the generation prompt from UI/API parameters;
- only include settings supported by that model/version;
- mention any uncertain or unsupported feature instead of silently assuming it works.

If no target model is specified, provide a model-agnostic master prompt and a short adaptation note. Do not output four redundant model versions unless requested.

### Step 8 — Quality check

Before returning, check:
- Does the prompt clearly state the subject and scene?
- Is the primary action concrete and physically plausible?
- Is camera movement compatible with the action?
- Are the timeline and duration consistent?
- Are lighting and palette coherent rather than contradictory?
- Are character, costume, prop, and environment continuity explicit where needed?
- Are audio instructions separated from visuals when the model may not support audio?
- Are model-specific parameters separated from prose?
- Are observations, inferences, and unknowns distinguished?
- Can the user replace the bracketed fields without needing to learn the whole method?

Revise if any answer is no.

## Standard output format

Unless the user asks for a shorter answer, return:

1. **Access status** — what media and audio were actually inspected.
2. **Creative summary** — premise, hook, emotional arc, memorable payoff.
3. **Shot-by-shot breakdown** — compact table.
4. **Why it works** — reusable visual/storytelling techniques.
5. **Fixed vs replaceable elements** — clear lists.
6. **Ready-to-use prompt** — final prompt for the requested new video.
7. **Model settings** — separate from prompt text; include only known/supported settings.
8. **Risks and next iteration** — the 2–4 most useful quality checks or likely failure points.

When the user asks only to create a skill, template, or workflow, provide that artifact instead of applying the full video analysis.

## Safety, copyright, and honesty

- Do not imply the user owns the reference video or has permission to reproduce protected material.
- For requests to make a new work, focus on high-level techniques and original expression rather than copying distinctive dialogue, lyrics, or a complete scene shot-for-shot.
- Do not reproduce long copyrighted dialogue or lyrics from the reference. Summarize them or use user-provided text where appropriate.
- Do not make up sources, timestamps, model features, or official documentation.
