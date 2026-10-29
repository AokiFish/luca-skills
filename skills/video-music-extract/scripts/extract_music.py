#!/usr/bin/env python3
"""Extract music as mp3 from any video URL, controlling whether human voice is kept.

Intent parameter (--intent, takes priority over --mode):
  pure    (default) instrumental-only: output has NO voice. Only runs Demucs
                      separation (no_vocals) when a voice is detected; if the
                      source is already instrumental it is extracted directly
                      (faster and leaves no separation artifacts).
  all              keep original lead vocals + ALL dubbing: extract the full
                      track, no separation at all.
  chorus           keep chorus (Chorus): when the source only has "ah"-style
                      backing/choir vocals, keep them too (extract full track).
                      NOTE: Demucs cannot split "lead" from "choir", so chorus
                      is mechanically the same as `all` (full track). If the
                      source also has real lead-lyrics, chorus keeps those too.

Advanced override:
  --mode extract|separate   explicitly set the low-level action, bypassing intent.

Features:
  - All external calls use subprocess list args; Unicode paths (incl. Chinese)
    are not mis-encoded by a legacy Windows Git-Bash shell.
  - Download lands on an ASCII temp name; only the final path is written via
    Python, avoiding mojibake filenames.
  - pure-intent voice detection reuses a local YAMNet (ONNX) model; if it is
    missing it is auto-downloaded from the HuggingFace mirror. Safe fallback to
    "separate" when the model/deps are unavailable.

Usage:
  python extract_music.py --url <URL> [--page N] [--intent pure|all|chorus]
                          [--out <path.mp3>] [--workdir <dir>]
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

# --------------------------------------------------------------------------
# Location helpers (ALL overridable via env vars -> portable across machines)
# --------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
LOCAL_ASSETS = os.path.join(SKILL_DIR, "assets")


def _env(name, default):
    return os.environ.get(name) or default


def resolve_tool(env_name, name):
    """Find an executable: env override first, then PATH lookup."""
    cand = []
    if os.environ.get(env_name):
        cand.append(os.environ[env_name])
    cand.append(name)
    for c in cand:
        if not c:
            continue
        if os.path.isfile(c):
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def _venv_python(venv):
    if os.name == "nt":
        return os.path.join(venv, "Scripts", "python.exe")
    return os.path.join(venv, "bin", "python")


def _venv_bin(venv, exe):
    if os.name == "nt":
        return os.path.join(venv, "Scripts", exe + ".exe")
    return os.path.join(venv, "bin", exe)


YTDLP = resolve_tool("VME_YTDLP", "yt-dlp")
FFMPEG = resolve_tool("VME_FFMPEG", "ffmpeg")
FFPROBE = resolve_tool("VME_FFPROBE", "ffprobe")

# Heavy-dependency virtualenv (torch/demucs/onnxruntime/...), auto-created on
# first use. Override with VME_VENV if you already have a suitable venv.
APP_VENV = _env("VME_VENV", os.path.join(SKILL_DIR, ".cache", "venv"))
DEMUCS = _venv_bin(APP_VENV, "demucs")

# YAMNet weights for voice detection (pure intent). Override with VME_YAMNET_DIR.
YAMNET_DIR = _env("VME_YAMNET_DIR", LOCAL_ASSETS)
YAMNET_ONNX = os.path.join(YAMNET_DIR, "yamnet.onnx")
YAMNET_CSV = os.path.join(YAMNET_DIR, "yamnet_class_map.csv")

# AudioSet class-name keywords treated as "human voice".
VOICE_KEYWORDS = ("speech", "sing", "vocal", "choir", "chorus", "rap",
                  "yodel", "hum", "beatbox", "inton", "conversation")


# --------------------------------------------------------------------------
# Voice detection (YAMNet)
# --------------------------------------------------------------------------
def ensure_yamnet():
    """Auto-download YAMNet weights to YAMNET_DIR if missing. Returns True if ready."""
    if os.path.isfile(YAMNET_ONNX) and os.path.isfile(YAMNET_CSV):
        return True
    try:
        import huggingface_hub as hh  # noqa
    except Exception:
        sys.stderr.write("[yamnet] huggingface_hub not installed; cannot auto-download.\n")
        return False
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.makedirs(YAMNET_DIR, exist_ok=True)
    for fn in ("yamnet.onnx", "yamnet_class_map.csv"):
        try:
            hh.hf_hub_download(repo_id="jafet21/yamnetonnx", filename=fn,
                               local_dir=os.path.abspath(YAMNET_DIR))
        except Exception as e:  # noqa
            sys.stderr.write("[yamnet] download failed: " + repr(e) + "\n")
            return False
    return True


def _sf_read(path):
    """Minimal wav reader: soundfile if available, else numpy+wave fallback."""
    try:
        import soundfile as sf
        return sf.read(path, dtype="float32")
    except Exception:
        import numpy as np
        import wave
        with wave.open(path, "rb") as w:
            n = w.getnframes()
            raw = w.readframes(n)
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            ch = w.getnchannels()
            if ch > 1:
                data = data.reshape(-1, ch).mean(axis=1)
            return data, w.getframerate()


def has_human_voice(wav):
    """Detect voice/singing with YAMNet.

    Returns (has_voice, top_label, max_score, frac).
    Combined criterion (more robust than max score alone):
      max per-frame voice score > 0.12  -- a strong vocal segment exists
      OR fraction of frames with voice>0.05 > 0.02  -- voice recurs steadily
        (real singing hits many frames; an instrument's occasional spike only
         hits scattered frames).

    If the model or deps are unavailable, returns (True, '<yamnet unavailable,
    safe fallback to separate>', 1.0, 0.0) so pure-intent safely separates and
    still yields instrumental output.
    """
    if not (os.path.isfile(YAMNET_ONNX) and os.path.isfile(YAMNET_CSV)):
        return True, "<yamnet weights missing, safe fallback to separate>", 1.0, 0.0
    try:
        import numpy as np
        import onnxruntime as ort
    except Exception:
        return True, "<onnxruntime unavailable, safe fallback to separate>", 1.0, 0.0
    sess = ort.InferenceSession(YAMNET_ONNX, providers=["CPUExecutionProvider"])
    names = []
    with open(YAMNET_CSV, encoding="utf-8") as f:
        for line in f.read().splitlines()[1:]:
            parts = line.split(",")
            if len(parts) >= 3:
                names.append(parts[2].strip())
    vidx = [i for i, n in enumerate(names)
            if any(k in n.lower() for k in VOICE_KEYWORDS)]
    data, sr = _sf_read(wav)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != 16000:
        data = np.interp(np.linspace(0, len(data), int(len(data) * 16000 / sr)),
                         np.arange(len(data)), data).astype(np.float32)
    scores = sess.run(None, {"waveform": data.astype(np.float32)})[0]  # [frames,521]
    voce = scores[:, vidx].max(axis=1)
    max_score = float(voce.max())
    frac = float((voce > 0.05).mean())
    best_i = int(voce.argmax())
    g = scores.max(axis=0)
    label = names[int(g.argmax())]
    has = (max_score > 0.12) or (frac > 0.02)
    return has, label, max_score, frac


# --------------------------------------------------------------------------
# Heavy-dependency venv (torch / demucs / onnxruntime / huggingface_hub / numpy)
# --------------------------------------------------------------------------
def ensure_venv():
    """Create the APP venv with all heavy deps on first use. Returns venv python."""
    global DEMUCS
    vpy = _venv_python(APP_VENV)
    if not os.path.isfile(vpy):
        print("[setup] creating venv at", APP_VENV, flush=True)
        os.makedirs(os.path.dirname(APP_VENV), exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", APP_VENV], check=True)
        subprocess.run([vpy, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        ok = subprocess.run([vpy, "-m", "pip", "install", "torch",
                             "--index-url", "https://download.pytorch.org/whl/cpu"]).returncode == 0
        if not ok:
            print("[setup] CPU torch install failed, falling back to default torch...", flush=True)
            subprocess.run([vpy, "-m", "pip", "install", "torch"], check=True)
        subprocess.run([vpy, "-m", "pip", "install",
                        "demucs", "onnxruntime", "numpy", "huggingface_hub"], check=True)
    # Make sure key deps are present (e.g. torch wheels differ across platforms).
    if subprocess.run([vpy, "-c", "import torch, demucs, onnxruntime, numpy, huggingface_hub"],
                      capture_output=True).returncode != 0:
        subprocess.run([vpy, "-m", "pip", "install",
                        "demucs", "onnxruntime", "numpy", "huggingface_hub"], check=True)
    DEMUCS = _venv_bin(APP_VENV, "demucs")
    return vpy


def reexec_in_venv():
    """Re-run this script under the APP venv python so onnxruntime is available."""
    vpy = ensure_venv()
    os.execv(vpy, [vpy, os.path.abspath(__file__)] + sys.argv[1:])


# --------------------------------------------------------------------------
# Pipeline steps
# --------------------------------------------------------------------------
def run(cmd, **kw):
    print("RUN:", " ".join(str(x) for x in cmd), flush=True)
    return subprocess.run(cmd, **kw)


def ensure_wav16k(src, workdir):
    out = os.path.join(workdir, "yamnet_in.wav")
    r = run([FFMPEG, "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
             "-f", "wav", out], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg resample failed:\n" + (r.stderr or r.stdout))
    return out


def download_audio(url, page, workdir):
    if not YTDLP:
        sys.exit("ERROR: yt-dlp not found. Install it (`pip install yt-dlp` or "
                 "`pipx install yt-dlp`) and put it on PATH, or set VME_YTDLP.")
    tpl = os.path.join(workdir, "audio.%(ext)s")
    if page:
        cmd = [YTDLP, "--playlist-items", str(page), "-f", "bestaudio",
               "--no-warnings", "-o", tpl, url]
    else:
        cmd = [YTDLP, "--no-playlist", "-f", "bestaudio",
               "--no-warnings", "-o", tpl, url]
    r = run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("yt-dlp failed:\n" + (r.stderr or r.stdout))
    candidates = [os.path.join(workdir, f) for f in os.listdir(workdir)
                  if f.startswith("audio.") and not f.endswith(".part")]
    if not candidates:
        sys.exit("no audio downloaded, dir: " + str(os.listdir(workdir)))
    candidates.sort(key=len)
    return candidates[-1]


def separate(inp, workdir):
    ensure_venv()  # make sure demucs + torch are installed
    demucs = DEMUCS
    out_dir = os.path.join(workdir, "demucs")
    # --two-stems=vocals is required to get no_vocals.wav (the instrumental).
    # Without it htdemucs only emits 4 stems (vocals/drums/bass/other), no no_vocals.
    cmd = [DEMUCS, "-n", "htdemucs", "--two-stems", "vocals", "-o", out_dir, inp]
    r = run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        print("[separate] HF direct failed, retry via mirror hf-mirror.com...", flush=True)
        r = run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("demucs failed:\n" + (r.stderr or r.stdout))
    stem = os.path.splitext(os.path.basename(inp))[0]
    base = os.path.join(out_dir, "htdemucs", stem)
    for ext in ("mp3", "m4a", "wav", "flac", "ogg"):
        p = os.path.join(base, "no_vocals." + ext)
        if os.path.isfile(p):
            return p
    found = glob.glob(os.path.join(out_dir, "**", "no_vocals.*"), recursive=True)
    if found:
        return found[0]
    sys.exit("no_vocals not found, dir: " + base)


def to_mp3(src, out):
    if not FFMPEG:
        sys.exit("ERROR: ffmpeg not found. Install FFmpeg and put it on PATH, "
                 "or set VME_FFMPEG.")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    # Write through an ASCII temp name in the same directory, then rename, so a
    # valid (but shell-mangled) --out never reaches ffmpeg as bytes.
    d = os.path.dirname(os.path.abspath(out))
    base, ext = os.path.splitext(os.path.basename(out))
    if all(ord(c) < 128 for c in base):
        tmp = None
        final = out
    else:
        tmp = os.path.join(d, "_vme_tmp" + (ext or ".mp3"))
        final = tmp
    cmd = [FFMPEG, "-y", "-i", src, "-vn", "-acodec", "libmp3lame",
           "-b:a", "256k", "-ar", "44100", "-map", "0:a:0", final]
    r = run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + (r.stderr or r.stdout))
    if tmp:
        os.replace(tmp, out)
    return out


def probe(path):
    if not FFPROBE:
        return None
    r = run([FFPROBE, "-v", "error", "-show_entries",
             "format=duration:stream=codec_name:stream=sample_rate",
             "-of", "default=noprint_wrappers=1", path],
            capture_output=True, text=True)
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--page", type=int, default=None, help="Bilibili multi-P index (p=N)")
    ap.add_argument("--intent", choices=["pure", "all", "chorus"], default="pure",
                    help="intent: pure=instrumental(default) / all=with voice+dubbing / chorus=keep choir")
    ap.add_argument("--mode", choices=["extract", "separate"], default=None,
                    help="advanced override: explicit low-level action")
    ap.add_argument("--out", required=True, help="final mp3 path")
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()

    # pure intent needs YAMNet voice detection; if onnxruntime is missing in the
    # current interpreter, re-run this script under the APP venv.
    if args.intent == "pure" and args.mode is None:
        try:
            import onnxruntime  # noqa
        except Exception:
            ensure_yamnet()
            reexec_in_venv()

    workdir = args.workdir or tempfile.mkdtemp(prefix="vme_")
    os.makedirs(workdir, exist_ok=True)

    audio = download_audio(args.url, args.page, workdir)

    if args.mode:
        mode = args.mode
    elif args.intent in ("all", "chorus"):
        mode = "extract"
        if args.intent == "chorus":
            print("[intent=chorus] extract full track; note Demucs cannot isolate "
                  "choir from lead, so real lead-lyrics (if any) are kept too.", flush=True)
    else:  # pure
        ensure_yamnet()
        w16 = ensure_wav16k(audio, workdir)
        hv, label, score, frac = has_human_voice(w16)
        print(f"[intent=pure] voice detection: has_voice={hv} (top={label} "
              f"max={score:.3f} frame_frac={frac:.3f})", flush=True)
        mode = "separate" if hv else "extract"

    print(f"[decision] intent={args.intent} -> mode={mode}", flush=True)
    src = separate(audio, workdir) if mode == "separate" else audio
    to_mp3(src, args.out)
    info = probe(args.out)
    print("DONE:", os.path.abspath(args.out))
    if info:
        print("INFO:\n" + info)


if __name__ == "__main__":
    main()
