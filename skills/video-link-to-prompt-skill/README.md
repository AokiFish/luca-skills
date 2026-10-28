# Video Link → Prompt Skill

A reusable Agent Skill for turning a reference video into:
- an evidence-grounded shot-by-shot breakdown;
- a concise analysis of the creative choices;
- fixed rules versus replaceable variables;
- a reusable cross-model master prompt;
- optional model-specific prompt/settings adaptation.

## Package layout

- `SKILL.md` — skill entrypoint and operating procedure.
- `references/analysis-checklist.md` — practical shot-analysis checklist.
- `references/model-adaptation.md` — cross-model adaptation rules.
- `templates/master-prompt.md` — reusable prompt skeleton.
- `templates/shot-breakdown.md` — shot table template.
- `templates/output-report.md` — final report structure.

## How to use

1. Install/import this folder into an Agent Skills-compatible environment.
2. Trigger it by pasting a video URL and asking for a breakdown, or by uploading a video.
3. State the target model and desired duration/aspect ratio if known.
4. If the video link cannot be accessed, upload the clip or provide key frames and a transcript.

## Important

The skill defines the analysis workflow; it does not itself grant browser, video-download, audio-transcription, or video-generation capabilities. The host agent must have suitable tools and permissions. It must report inaccessible media rather than hallucinating a breakdown.

## Compatibility

The package follows the common Agent Skills convention: a skill folder with a `SKILL.md` entrypoint and optional supporting files. Specific platforms may require their own installation path or packaging conventions.
