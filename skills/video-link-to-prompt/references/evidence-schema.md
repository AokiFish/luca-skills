# Evidence bundle schema v1

`analysis_bundle.json` contains:
- `schema_version`: schema identifier.
- `status`: `ok`, `partial`, or `failed`.
- `source`: source type and URL/path.
- `media`: duration, dimensions, fps, audio presence where available.
- `extraction`: sampling interval, frame count, audio/transcription status.
- `frames`: ordered records with index, timestamp, filename and label.
- `files`: contact sheet, audio and transcript paths where available.
- `notes`: technical limitations and warnings.

This bundle records extracted data; it does not contain semantic claims about what the video depicts.
