# Image Reverse Engineering Skill v3

This version upgrades the workflow from broad image description to spatially grounded, relationship-aware prompt compilation.

## Included
- `SKILL.md`: cross-agent instructions and required output contract.
- `scripts/analyze_image.py`: executable technical image analysis plus optional OpenAI-compatible vision endpoint.
- `schemas/analysis.schema.json`: machine-readable report schema.
- `examples/sample-output.json`: illustrative report shape.
- `requirements.txt`: Pillow dependency.

## Install
```bash
python -m pip install -r requirements.txt
```

## Technical-only run
```bash
python scripts/analyze_image.py ./reference.jpg --out analysis.json
```
This measures image properties but does not understand scene semantics.

## Vision-assisted run
Linux/macOS:
```bash
export VISION_API_KEY="YOUR_KEY"
export VISION_BASE_URL="https://api.openai.com/v1"
export VISION_MODEL="YOUR_VISION_CAPABLE_MODEL"
python scripts/analyze_image.py ./reference.jpg --vision --out analysis.json
```
Windows PowerShell:
```powershell
$env:VISION_API_KEY="YOUR_KEY"
$env:VISION_BASE_URL="https://api.openai.com/v1"
$env:VISION_MODEL="YOUR_VISION_CAPABLE_MODEL"
python .\scripts\analyze_image.py .\reference.jpg --vision --out analysis.json
```
The endpoint must accept image input in an OpenAI-compatible chat-completions request. Provider-specific adapters may be needed.

## What v3 changes
- Requires approximate spatial anchors when placement matters.
- Captures depth-plane and focus relationships, not just object names.
- Separates observed, inferred, and unknown information.
- Ranks must-preserve visual anchors.
- Audits contradictions such as head direction versus gaze or bright backlight versus exposure.
- Uses robust visual constraints instead of brittle over-precise instructions.
- Compiles one platform-neutral prompt by default, with platform-specific variants only when needed.

## Limits
No universal Skill can bypass a host agent's lack of image access, vision capability, or execution permission. The core is portable; installation and API adapters can vary by host.
