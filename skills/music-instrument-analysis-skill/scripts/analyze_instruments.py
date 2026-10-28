#!/usr/bin/env python3
"""Instrument-recognition helper (two-layer + timeline segmentation).

Layer 1 (objective): YAMNet (ONNX, AudioSet 521 classes) classifies the waveform
  frame-by-frame, producing an objective presence probability per instrument /
  sound class. Weights + class map live in ../assets/.
Layer 2 (knowledge): spectral features (band-energy ratios / centroid / onsets)
  + genre knowledge let the AI make the final call and write the explanation.

Two output granularities:
  - Whole track: everything merged ("which instruments appear").
  - Timeline segments (--seg-len>0, default 8s): fixed windows, per-segment
    instruments + spectrum, then merged into natural passages (Intro / VerseN /
    Bridge / Outro, all labeled "inferred").

Instrument names = YAMNet probability (objective) + spectral features + genre
knowledge (subjective correction).

Dependencies: numpy / scipy / matplotlib / onnxruntime + system ffmpeg.
All external calls use subprocess list args; non-ASCII paths are copied to an
ASCII temp name first to avoid Windows GBK mojibake.

Usage:
  python analyze_instruments.py --audio <file.mp3|wav> --out <stats.json> \
        [--png <spec.png>] [--seg-len 8]
  python analyze_instruments.py --url  <video URL>  --out <stats.json> [--seg-len 8]
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, find_peaks
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# --------------------------------------------------------------------------
# Location helpers (env-overridable -> portable)
# --------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
YAMNET_ONNX = os.path.join(ASSETS_DIR, "yamnet.onnx")
YAMNET_CSV = os.path.join(ASSETS_DIR, "yamnet_class_map.csv")


def resolve_tool(env_name, name):
    if os.environ.get(env_name):
        if os.path.isfile(os.environ[env_name]):
            return os.environ[env_name]
        found = shutil.which(os.environ[env_name])
        if found:
            return found
    found = shutil.which(name)
    return found


FFMPEG = resolve_tool("MIA_FFMPEG", "ffmpeg")
FFPROBE = resolve_tool("MIA_FFPROBE", "ffprobe")
YTDLP = resolve_tool("MIA_YTDLP", "yt-dlp")

# 乐器/声音类别关键词 -> (中文名, 族)。从 521 个 AudioSet 类里筛出音乐相关项。
INSTRUMENT_MAP = [
    # 键盘
    ("piano", "钢琴", "键盘"),
    ("keyboard", "键盘", "键盘"),
    ("organ", "管风琴/电子琴", "键盘"),
    ("synthesizer", "合成器", "键盘"),
    ("harpsichord", "羽管键琴", "键盘"),
    ("accordion", "手风琴", "键盘"),
    # 吉他/弹拨
    ("guitar", "吉他", "弹拨"),
    ("banjo", "班卓琴", "弹拨"),
    ("mandolin", "曼陀林", "弹拨"),
    ("ukulele", "尤克里里", "弹拨"),
    ("sitar", "西塔琴", "弹拨"),
    ("lute", "鲁特琴", "弹拨"),
    ("zither", "齐特琴", "弹拨"),
    ("koto", "筝", "弹拨"),
    ("guzheng", "古筝", "弹拨"),
    ("shamisen", "三味线", "弹拨"),
    # 贝斯
    ("bass guitar", "电贝斯", "贝斯"),
    ("double bass", "低音提琴", "贝斯"),
    ("electric bass", "电贝斯", "贝斯"),
    ("contrabass", "低音提琴", "贝斯"),
    # 弦乐
    ("violin", "小提琴", "弦乐"),
    ("fiddle", "小提琴", "弦乐"),
    ("viola", "中提琴", "弦乐"),
    ("cello", "大提琴", "弦乐"),
    ("string section", "弦乐组", "弦乐"),
    ("bowed string", "弓弦乐", "弦乐"),
    ("erhu", "二胡", "弦乐"),
    # 木管
    ("flute", "长笛", "木管"),
    ("clarinet", "单簧管", "木管"),
    ("oboe", "双簧管", "木管"),
    ("bassoon", "巴松管", "木管"),
    ("recorder", "竖笛", "木管"),
    ("piccolo", "短笛", "木管"),
    ("saxophone", "萨克斯", "木管"),
    # 铜管
    ("trumpet", "小号", "铜管"),
    ("horn", "圆号", "铜管"),
    ("trombone", "长号", "铜管"),
    ("tuba", "大号", "铜管"),
    ("cornet", "短号", "铜管"),
    ("flugelhorn", "柔音号", "铜管"),
    ("brass", "铜管乐", "铜管"),
    # 打击/鼓
    ("drum kit", "架子鼓", "打击"),
    ("drum", "鼓", "打击"),
    ("snare", "军鼓", "打击"),
    ("bass drum", "底鼓", "打击"),
    ("cymbal", "镲", "打击"),
    ("hi-hat", "踩镲", "打击"),
    ("percussion", "打击乐", "打击"),
    ("timpani", "定音鼓", "打击"),
    ("marimba", "马林巴", "打击"),
    ("xylophone", "木琴", "打击"),
    ("vibraphone", "颤音琴", "打击"),
    ("gong", "锣", "打击"),
    ("tabla", "塔布拉鼓", "打击"),
    ("steelpan", "钢鼓", "打击"),
    ("bell", "钟/铃", "打击"),
    ("chime", "编钟", "打击"),
    ("tambourine", "铃鼓", "打击"),
    ("conga", "康加鼓", "打击"),
    ("bongo", "邦戈鼓", "打击"),
    ("taiko", "太鼓", "打击"),
    # 竖琴
    ("harp", "竖琴", "竖琴"),
    # 其他民族/色彩
    ("harmonica", "口琴", "色彩"),
    ("bagpipe", "风笛", "色彩"),
    ("didgeridoo", "迪吉里杜管", "色彩"),
    # 人声（非乐器，但用于判断"是否纯音乐"）
    ("singing", "人声/演唱", "人声"),
    ("singer", "人声/演唱", "人声"),
    ("choir", "合唱", "人声"),
    ("vocal", "人声", "人声"),
    ("opera", "歌剧人声", "人声"),
    ("rap", "说唱", "人声"),
    ("beatbox", "口技", "人声"),
    ("speech", "语音", "人声"),
    ("narration", "旁白", "人声"),
]


def _ascii_safe(path):
    """If the file name has non-ASCII (Chinese, etc.), copy to an ASCII temp
    name first to avoid ffmpeg GBK-mojibake on legacy Windows shells."""
    if all(ord(c) < 128 for c in os.path.basename(path)):
        return path
    tmp = tempfile.mkdtemp(prefix="mia_")
    ext = os.path.splitext(path)[1] or ".tmp"
    dst = os.path.join(tmp, "input" + ext)
    shutil.copy(path, dst)
    return dst


def _agg_instruments(max_scores, names):
    """Aggregate [521] scores into an instrument list + family aggregation +
    has_voice. Shared by whole-track and segment modes."""
    fam_best = {}
    detail = []
    for idx, sc in enumerate(max_scores):
        nm = names.get(idx, "")
        low = nm.lower()
        for key, zh, fam in INSTRUMENT_MAP:
            if key in low:
                detail.append((zh, nm, float(sc), fam))
                fam_best[fam] = max(fam_best.get(fam, 0.0), float(sc))
                break
    best = {}
    for zh, nm, sc, fam in detail:
        if zh not in best or sc > best[zh][1]:
            best[zh] = (nm, sc, fam)
    instruments = sorted(
        [{"name": zh, "class": v[0], "score": round(v[1], 3), "family": v[2]}
         for zh, v in best.items() if v[1] >= 0.05],
        key=lambda x: x["score"], reverse=True
    )
    families = sorted(
        [{"family": k, "score": round(v, 3)} for k, v in fam_best.items() if v >= 0.05],
        key=lambda x: x["score"], reverse=True
    )
    has_voice = any(fam == "人声" and v >= 0.1 for fam, v in fam_best.items())
    return instruments, families, has_voice


def to_wav(src, dst):
    if not FFMPEG:
        sys.exit("ERROR: ffmpeg not found. Install FFmpeg on PATH or set MIA_FFMPEG.")
    # Mono + 16 kHz (YAMNet needs 16k; spectral band thresholds still hold at 16k)
    r = subprocess.run([FFMPEG, "-y", "-i", src, "-ac", "1", "-ar", "16000", dst],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg transcode failed:\n" + (r.stderr or r.stdout))
    if not os.path.isfile(dst):
        sys.exit("ffmpeg produced no wav: " + dst)


def download_audio(url, workdir):
    if not YTDLP:
        sys.exit("ERROR: yt-dlp not found. Install yt-dlp (`pip install yt-dlp`) "
                 "and put it on PATH, or set MIA_YTDLP.")
    tpl = os.path.join(workdir, "audio.%(ext)s")
    r = subprocess.run([YTDLP, "--no-playlist", "-f", "bestaudio",
                        "--no-warnings", "-o", tpl, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("yt-dlp failed:\n" + (r.stderr or r.stdout))
    candidates = [os.path.join(workdir, f) for f in os.listdir(workdir)
                  if f.startswith("audio.") and not f.endswith(".part")]
    if not candidates:
        sys.exit("no audio downloaded, dir: " + str(os.listdir(workdir)))
    candidates.sort(key=len)
    return candidates[-1]


def _read_mono(wav):
    sr, data = wavfile.read(wav)
    if data.ndim > 1:
        data = data[:, 0]
    if data.dtype != np.float32:
        info = np.iinfo(data.dtype)
        data = data.astype(np.float32) / max(info.max, 1)
    return sr, data


def analyze_spectrum(wav):
    sr, data = _read_mono(wav)
    dur = len(data) / sr

    f, t, Z = stft(data, fs=sr, nperseg=1024, noverlap=512)
    mag = np.abs(Z)
    power = mag ** 2
    tot = power.sum() + 1e-12

    low = power[f < 200].sum()
    mid = power[(f >= 200) & (f < 2000)].sum()
    high = power[f >= 2000].sum()

    centroid = (f[:, None] * power).sum(axis=0) / (power.sum(axis=0) + 1e-12)
    centroid_mean = float(np.mean(centroid))

    env = mag.sum(axis=0)
    env = env / (env.max() + 1e-12)
    peaks, _ = find_peaks(env, height=0.3, distance=8)
    onsets = len(peaks)

    rms = float(np.sqrt(np.mean(data ** 2)))

    return {
        "duration_s": round(dur, 2),
        "sample_rate": sr,
        "low_ratio": round(float(low / tot), 3),
        "mid_ratio": round(float(mid / tot), 3),
        "high_ratio": round(float(high / tot), 3),
        "spectral_centroid_hz": round(centroid_mean, 1),
        "onsets": onsets,
        "onset_rate_per_s": round(onsets / max(dur, 1), 2),
        "rms": round(rms, 4),
    }


def plot(wav, out_png):
    sr, data = _read_mono(wav)
    f, t, Z = stft(data, fs=sr, nperseg=1024, noverlap=512)
    S = np.log1p(np.abs(Z))
    plt.figure(figsize=(10, 4))
    plt.imshow(S, aspect="auto", origin="lower", cmap="magma",
               extent=[t.min(), t.max(), f.min(), f.max()])
    plt.colorbar(format="%.1f")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Log-magnitude spectrogram")
    plt.tight_layout()
    plt.savefig(out_png, dpi=110)
    plt.close()


def load_class_map(csv_path):
    name_by_index = {}
    with open(csv_path, encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) < 3 or not row[0].isdigit():
                continue
            idx = int(row[0])
            name_by_index[idx] = row[2].strip().strip('"')
    return name_by_index


def _ensure_yamnet():
    """Download YAMNet weights to ASSETS_DIR if missing (one-time). Returns ready."""
    if os.path.isfile(YAMNET_ONNX) and os.path.isfile(YAMNET_CSV):
        return True
    try:
        import huggingface_hub as hh
    except Exception:
        sys.stderr.write("[yamnet] huggingface_hub missing; cannot auto-download.\n")
        return False
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for fn in ("yamnet.onnx", "yamnet_class_map.csv"):
        try:
            hh.hf_hub_download(repo_id="jafet21/yamnetonnx", filename=fn,
                               local_dir=os.path.abspath(ASSETS_DIR))
        except Exception as e:  # noqa
            sys.stderr.write("[yamnet] download failed: " + repr(e) + "\n")
            return False
    return True


def _yamnet_scores(wav):
    """Run YAMNet; return per-frame scores, class names, frame duration, total
    duration, 16k waveform, sample rate."""
    import onnxruntime as ort
    sr, data = _read_mono(wav)
    if sr != 16000:
        n = int(round(len(data) * 16000 / sr))
        data = np.interp(np.linspace(0, len(data) - 1, n), np.arange(len(data)), data).astype(np.float32)
    waveform = data.astype(np.float32)
    sess = ort.InferenceSession(YAMNET_ONNX, providers=["CPUExecutionProvider"])
    scores, _emb, _mel = sess.run(None, {"waveform": waveform})
    F = scores.shape[0]
    dur = len(waveform) / 16000
    frame_dur = dur / F if F else 0.48
    names = load_class_map(YAMNET_CSV)
    return scores, names, frame_dur, dur, waveform, 16000


def analyze_yamnet(wav):
    """Layer 1 (whole track): YAMNet objective instrument/sound probabilities."""
    try:
        import onnxruntime as ort  # noqa
    except Exception as e:
        return {"available": False, "error": "onnxruntime not installed: " + repr(e)}

    if not _ensure_yamnet():
        return {"available": False, "error": "YAMNet weights/map missing or download failed"}

    scores, names, _fd, _dur, _w, _sr = _yamnet_scores(wav)
    max_scores = scores.max(axis=0)
    instruments, families, has_voice = _agg_instruments(max_scores, names)
    return {
        "available": True,
        "model": "YAMNet (ONNX, AudioSet 521-class)",
        "instruments": instruments[:15],
        "families": families,
        "has_voice": has_voice,
    }


def _spectrum_features_arr(seg, sr):
    """Spectral features for a waveform array (same口径 as analyze_spectrum)."""
    if len(seg) < sr * 0.5:
        return {"low_ratio": 0.0, "mid_ratio": 0.0, "high_ratio": 0.0,
                "spectral_centroid_hz": 0.0, "onset_rate_per_s": 0.0, "rms": 0.0,
                "too_short": True}
    f, t, Z = stft(seg, fs=sr, nperseg=1024, noverlap=512)
    mag = np.abs(Z)
    power = mag ** 2
    tot = power.sum() + 1e-12
    low = power[f < 200].sum()
    mid = power[(f >= 200) & (f < 2000)].sum()
    high = power[f >= 2000].sum()
    centroid = (f[:, None] * power).sum(axis=0) / (power.sum(axis=0) + 1e-12)
    env = mag.sum(axis=0)
    env = env / (env.max() + 1e-12)
    peaks, _ = find_peaks(env, height=0.3, distance=8)
    rms = float(np.sqrt(np.mean(seg ** 2)))
    dur = len(seg) / sr
    return {
        "low_ratio": round(float(low / tot), 3),
        "mid_ratio": round(float(mid / tot), 3),
        "high_ratio": round(float(high / tot), 3),
        "spectral_centroid_hz": round(float(np.mean(centroid)), 1),
        "onset_rate_per_s": round(len(peaks) / max(dur, 1), 2),
        "rms": round(rms, 4),
    }


def _spectrum_infer(feat, hit_fams=None):
    """Layer 2 fallback: infer broad instrument classes from band-energy ratios,
    tagged source=spectrum. Skipped when YAMNet already hit the family (avoids
    duplicates). Recovers soft tracks where piano/strings/bass are under-detected."""
    hit_fams = hit_fams or set()
    out = []
    if feat.get("too_short"):
        return out
    low, mid, high = feat["low_ratio"], feat["mid_ratio"], feat["high_ratio"]
    ons = feat.get("onset_rate_per_s", 0)
    if low >= 0.45 and "贝斯" not in hit_fams:
        out.append(("贝斯/低音 (频谱推断)", "贝斯", max(0.5, low)))
    if ons >= 1.5 and low >= 0.38 and "打击" not in hit_fams:
        out.append(("鼓/打击 (频谱推断)", "打击", 0.6))
    if mid >= 0.28 and not (hit_fams & {"键盘", "弦乐"}):
        out.append(("钢琴/弦乐铺底 (频谱推断)", "键盘/弦乐", 0.5))
    if high >= 0.14 and "色彩" not in hit_fams:
        out.append(("高频色彩·铃/笛/竖琴 (频谱推断)", "色彩", 0.4))
    return out


def analyze_segments(wav, seg_len=8.0):
    """Timeline mode: fixed windows, per-segment instruments + spectrum."""
    scores, names, frame_dur, dur, data, sr = _yamnet_scores(wav)
    n = max(1, int(np.ceil(dur / seg_len)))
    segs = []
    for i in range(n):
        t0 = i * seg_len
        t1 = min((i + 1) * seg_len, dur)
        f0 = max(0, int(t0 / frame_dur))
        f1 = max(f0 + 1, int(t1 / frame_dur))
        seg_scores = scores[f0:f1]
        if len(seg_scores) == 0:
            seg_scores = scores[f0:f0 + 1]
        seg_max = seg_scores.max(axis=0)
        inst, fams, hv = _agg_instruments(seg_max, names)
        a = int(t0 * sr)
        b = int(t1 * sr)
        sfeat = _spectrum_features_arr(data[a:b], sr)
        hit_fams = {x["family"] for x in inst if x.get("score", 0) >= 0.1}
        for nm, fam, sc in _spectrum_infer(sfeat, hit_fams):
            inst.append({"name": nm, "class": "spectrum-inferred",
                         "score": round(sc, 3), "family": fam, "source": "spectrum"})
        segs.append({
            "start": round(t0, 1),
            "end": round(t1, 1),
            "instruments": inst[:10],
            "families": fams,
            "has_voice": hv,
            **sfeat,
        })
    return segs


def _cluster_sim(a, b):
    """Neighbor-segment similarity: instrument-set Jaccard + onset/low consistency."""
    sa = {x["name"] for x in a.get("instruments", [])}
    sb = {x["name"] for x in b.get("instruments", [])}
    j = len(sa & sb) / max(1, len(sa | sb)) if (sa or sb) else 1.0
    oa, ob = a.get("onset_rate_per_s", 0), b.get("onset_rate_per_s", 0)
    ocons = 1.0 - min(1.0, abs(oa - ob) / max(1.0, max(oa, ob)))
    la, lb = a.get("low_ratio", 0), b.get("low_ratio", 0)
    lcons = 1.0 - min(1.0, abs(la - lb) / max(0.5, max(la, lb)))
    return 0.5 * j + 0.25 * ocons + 0.25 * lcons


def cluster_structure(segments):
    """Merge similar neighbor segments into natural passages, give heuristic
    semantic names (all labeled "inferred").

    Naming (conservative, readable, not forced into pop form):
      - first segment -> Intro
      - last segment  -> Outro
      - sharp onset drop -> Bridge/Interlude
      - others -> Verse1/Verse2/... (sequential numbering)
    """
    clusters = []
    for seg in segments:
        if not clusters:
            clusters.append([seg])
            continue
        if _cluster_sim(clusters[-1][-1], seg) > 0.62:
            clusters[-1].append(seg)
        else:
            clusters.append([seg])

    all_onset = [s.get("onset_rate_per_s", 0) for s in segments if not s.get("too_short")]
    base_onset = float(np.mean(all_onset)) if all_onset else 0.0

    structure = []
    n = len(clusters)
    verse_idx = 0
    for i, cl in enumerate(clusters):
        start = cl[0]["start"]
        end = cl[-1]["end"]
        inst_counter = {}
        fam_sum = {}
        fam_cnt = {}
        onset_vals = []
        for s in cl:
            for x in s.get("instruments", []):
                if x.get("source") != "spectrum" and x.get("score", 0) < 0.1:
                    continue
                d = inst_counter.setdefault(x["name"], [0, 0.0, x["family"]])
                d[0] += 1
                d[1] += x.get("score", 0.5)
            for fm in s.get("families", []):
                fam_sum[fm["family"]] = fam_sum.get(fm["family"], 0.0) + fm["score"]
                fam_cnt[fm["family"]] = fam_cnt.get(fm["family"], 0) + 1
            if not s.get("too_short"):
                onset_vals.append(s.get("onset_rate_per_s", 0))
        min_appear = max(1, len(cl) // 2)
        top_inst = sorted(
            [{"name": k, "appear_segs": v[0], "avg_score": round(v[1] / v[0], 3),
              "family": v[2]}
             for k, v in inst_counter.items() if v[0] >= min_appear],
            key=lambda x: (x["appear_segs"], x["avg_score"]), reverse=True
        )[:6]
        fams = sorted(
            [{"family": k, "score": round(v / fam_cnt[k], 3)} for k, v in fam_sum.items()],
            key=lambda x: x["score"], reverse=True
        )
        cl_onset = float(np.mean(onset_vals)) if onset_vals else 0.0
        fam_set = {f["family"] for f in fams}
        has_perc = any(f["family"] == "打击" and f["score"] >= 0.2 for f in fams)
        sparse = (cl_onset < base_onset * 0.6) and not (has_perc and cl_onset >= base_onset * 0.5)
        if i == 0:
            label, reason = "前奏 (Intro, 推断)", "段落起始，配器较空/铺底为主"
        elif i == n - 1:
            label, reason = "尾奏 (Outro, 推断)", "段落收尾"
        elif sparse:
            label, reason = "桥段/间奏 (Bridge, 推断)", \
                f"鼓密度骤降(onset {cl_onset:.2f} < 基准 {base_onset:.2f})"
        else:
            verse_idx += 1
            label, reason = f"主歌{verse_idx} (Verse, 推断)", "配器较饱满且非特殊段"
        structure.append({
            "start": start,
            "end": end,
            "label": label,
            "reason": reason,
            "families": fams,
            "top_instruments": top_inst,
            "onset_rate_per_s": round(cl_onset, 2),
        })
    return structure


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=None, help="input audio (mp3/wav/...)")
    ap.add_argument("--url", default=None, help="video URL (downloaded via yt-dlp)")
    ap.add_argument("--out", required=True, help="feature-stats JSON output")
    ap.add_argument("--png", default=None, help="spectrogram PNG output")
    ap.add_argument("--no-yamnet", action="store_true", help="skip YAMNet layer")
    ap.add_argument("--seg-len", type=float, default=8.0,
                    help="timeline segment length (s); 0 disables segmentation; default 8")
    args = ap.parse_args()

    if not args.audio and not args.url:
        sys.exit("ERROR: provide --audio <file> or --url <video URL>")
    if args.audio and args.url:
        sys.exit("ERROR: provide only one of --audio / --url")

    tmp = tempfile.mkdtemp(prefix="mia_")
    if args.url:
        src = download_audio(args.url, tmp)
    else:
        src = args.audio
    safe = _ascii_safe(src)
    wav = os.path.join(tmp, "a.wav")
    to_wav(safe, wav)

    stats = analyze_spectrum(wav)
    png = args.png or (os.path.splitext(args.out)[0] + ".png")
    plot(wav, png)

    if not args.no_yamnet:
        stats["yamnet"] = analyze_yamnet(wav)
        if args.seg_len and args.seg_len > 0:
            stats["segments"] = analyze_segments(wav, args.seg_len)
            stats["structure"] = cluster_structure(stats["segments"])

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=2)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("PNG:", png)


if __name__ == "__main__":
    main()
