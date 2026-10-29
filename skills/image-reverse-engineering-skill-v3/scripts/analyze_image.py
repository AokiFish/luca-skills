#!/usr/bin/env python3
"""Technical image metrics and optional semantic report via an OpenAI-compatible vision API."""
from __future__ import annotations
import argparse, base64, json, mimetypes, os, sys, urllib.error, urllib.request
from pathlib import Path
from PIL import Image, ImageStat, ImageFilter, ImageOps

VISION_PROMPT = r"""Analyze the supplied image for faithful image-generation reproduction. Return valid JSON only:
{
 "scene_summary": "...",
 "frame": {"width": 0, "height": 0, "aspect_ratio": 0, "shot_scale": "...", "single_scene": true},
 "visual_fingerprint": [{"feature":"...", "importance":"must_preserve|secondary", "evidence":"..."}],
 "spatial_map": [
   {"element":"...", "approx_location":"...", "approx_size":"...", "depth_plane":"foreground|subject_plane|background|uncertain", "focus":"sharp|soft|blurred|uncertain", "relations":["..."], "confidence":"high|medium|low"}
 ],
 "pose_and_gaze": {"head_orientation":"...", "gaze_direction":"...", "expression":"...", "confidence":"high|medium|low"},
 "observed": [{"claim":"...", "confidence":"high|medium"}],
 "inferred": [{"claim":"...", "confidence":"high|medium|low", "why":"..."}],
 "unknown": ["..."],
 "lighting": {"key_direction":"...", "fill":"...", "backlight":"...", "shadow_behavior":"...", "highlight_behavior":"..."},
 "palette": [{"color_name":"...", "approx_hex":"#RRGGBB", "role":"..."}],
 "materials_textures": [{"material":"...", "visible_cues":"..."}],
 "prompt_en": "...",
 "drift_prevention": ["..."],
 "contradiction_audit": [{"issue":"...", "resolution":"..."}]
}
Use approximate ranges, not fake precision. Distinguish observed from inferred. Do not guess exact generator, source prompt, camera, lens, seed, or dynasty as fact. Describe head direction separately from gaze. Prioritize framing, spatial relationships, focus planes, lighting, and signature details. Keep the prompt coherent and avoid redundant adjectives. If uncertain, say so."""

def hexrgb(rgb):
    return "#" + "".join(f"{max(0,min(255,int(x))):02X}" for x in rgb)

def analyze(path: Path):
    with Image.open(path) as original:
        img = ImageOps.exif_transpose(original).convert("RGB")
        w,h = img.size
        small = img.copy()
        small.thumbnail((512,512))
        stat = ImageStat.Stat(small)
        gray = small.convert("L")
        gs = ImageStat.Stat(gray)
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_mean = ImageStat.Stat(edges).mean[0]
        # Quantized palette, based on actual quantizer palette indexes.
        q = small.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
        counts = sorted(q.getcolors(maxcolors=512*512) or [], reverse=True)
        pal = q.getpalette() or []
        colors=[]
        for count, idx in counts:
            if idx*3+2 >= len(pal): continue
            rgb=tuple(pal[idx*3:idx*3+3])
            hx=hexrgb(rgb)
            if any(x["hex"] == hx for x in colors): continue
            colors.append({"hex":hx,"share_estimate":round(count/(small.width*small.height),3)})
            if len(colors)==8: break
        return {
          "file":path.name,"mime_type":mimetypes.guess_type(path.name)[0] or "application/octet-stream",
          "dimensions":{"width":w,"height":h},"aspect_ratio":round(w/h,4),
          "orientation":"landscape" if w>h else "portrait" if h>w else "square",
          "file_size_bytes":path.stat().st_size,
          "technical_metrics":{
            "mean_rgb":[round(x,2) for x in stat.mean],
            "rgb_stddev":[round(x,2) for x in stat.stddev],
            "mean_luminance_0_255":round(gs.mean[0],2),
            "grayscale_contrast_stddev":round(gs.stddev[0],2),
            "edge_strength_proxy":round(edge_mean,2),
            "note":"These are technical heuristics, not semantic understanding or aesthetic scores."
          },
          "dominant_palette_estimate":colors,
          "semantic_analysis":None
        }

def vision(path: Path):
    key=os.environ.get("VISION_API_KEY")
    base=os.environ.get("VISION_BASE_URL","https://api.openai.com/v1").rstrip("/")
    model=os.environ.get("VISION_MODEL")
    if not key or not model:
        raise RuntimeError("--vision requires VISION_API_KEY and VISION_MODEL.")
    mime=mimetypes.guess_type(path.name)[0] or "image/jpeg"
    if not mime.startswith("image/"): mime="image/jpeg"
    data_url="data:"+mime+";base64,"+base64.b64encode(path.read_bytes()).decode()
    body={"model":model,"temperature":0.2,"messages":[
      {"role":"system","content":VISION_PROMPT},
      {"role":"user","content":[{"type":"text","text":"Analyze this reference image using the required JSON structure."},{"type":"image_url","image_url":{"url":data_url}}]}
    ]}
    req=urllib.request.Request(base+"/chat/completions",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=120) as r: obj=json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Vision API HTTP {e.code}: {e.read().decode(errors='replace')[:1500]}") from e
    content=obj["choices"][0]["message"]["content"]
    if isinstance(content,list): content="\n".join(x.get("text","") for x in content if isinstance(x,dict))
    content=content.strip()
    if content.startswith("```"):
        content=content.split("\n",1)[-1]
        if content.endswith("```"): content=content[:-3]
    try: return json.loads(content)
    except json.JSONDecodeError: return {"raw_model_response":content,"warning":"Provider response was not valid JSON."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("image",help="Path to image file")
    p.add_argument("--vision",action="store_true",help="Use configured vision API")
    p.add_argument("--out",help="Write JSON report to file")
    a=p.parse_args()
    path=Path(a.image).expanduser().resolve()
    if not path.is_file(): p.error(f"File not found: {path}")
    try:
        report=analyze(path)
        if a.vision: report["semantic_analysis"]=vision(path)
        else: report["semantic_analysis_status"]="not_run: technical metrics only"
        output=json.dumps(report,ensure_ascii=False,indent=2)
        if a.out:
            Path(a.out).write_text(output+"\n",encoding="utf-8")
            print(f"Wrote {a.out}",file=sys.stderr)
        else: print(output)
    except Exception as e:
        print("Error: "+str(e),file=sys.stderr); sys.exit(2)
if __name__=="__main__": main()
