#!/usr/bin/env python3
"""Optional adapter for an OpenAI-compatible multimodal endpoint that supports image inputs."""
import argparse, base64, json, os, sys
from pathlib import Path
import requests

SYSTEM = """Analyze timestamped keyframes from a reference video. Frames are samples, not continuous footage. Return: premise/hook/payoff; ordered beats tied to visible timestamps; possible shot boundaries with confidence; subjects/environment/props/continuity; framing/camera movement only where supported; lighting/color; transferable high-level methods; unknowns and suggested additional evidence. Separate observed, inferred and unknown. Do not infer exact camera gear, original prompts, seeds or hidden generation settings."""

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--bundle',required=True); ap.add_argument('--out',required=True); ap.add_argument('--max-frames',type=int,default=16); ap.add_argument('--timeout',type=int,default=180); args=ap.parse_args()
    key=os.getenv('OPENAI_API_KEY'); model=os.getenv('VISION_MODEL'); base=os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1').rstrip('/')
    if not key or not model: print('Missing OPENAI_API_KEY or VISION_MODEL; no API call made.',file=sys.stderr); return 2
    bundle_path=Path(args.bundle).expanduser().resolve(); bundle=json.loads(bundle_path.read_text(encoding='utf-8')); frames=bundle.get('frames',[])
    if not frames: print('Bundle contains no extracted frames.',file=sys.stderr); return 3
    n=min(max(1,args.max_frames),len(frames)); indexes=[round(i*(len(frames)-1)/(n-1)) for i in range(n)] if n>1 else [0]; selected=[frames[i] for i in indexes]
    content=[{'type':'text','text':'Analyze these keyframes chronologically. They are samples, not continuous footage. Metadata: '+json.dumps({'duration_seconds':bundle.get('media',{}).get('duration_seconds'),'sampling_interval_seconds':bundle.get('extraction',{}).get('sampling_interval_seconds'),'audio_extracted':bundle.get('extraction',{}).get('audio_extracted')})}]
    used=[]
    for item in selected:
        path=(bundle_path.parent/item['filename']).resolve()
        if not path.is_file(): continue
        encoded=base64.b64encode(path.read_bytes()).decode('ascii')
        content.extend([{'type':'text','text':f"Frame timestamp: {item.get('timestamp_seconds')} seconds; file: {item.get('filename')}"},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+encoded,'detail':'high'}}]); used.append(item)
    payload={'model':model,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':content}],'temperature':0.2}
    endpoint=base+'/chat/completions'
    try:
        response=requests.post(endpoint,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=payload,timeout=args.timeout)
        if response.status_code>=400: result={'status':'failed','http_status':response.status_code,'error':response.text[:5000],'model':model,'endpoint':endpoint}
        else:
            data=response.json(); result={'status':'ok','model':model,'endpoint':endpoint,'selected_frames':[{'timestamp_seconds':x.get('timestamp_seconds'),'filename':x.get('filename')} for x in used],'analysis':data.get('choices',[{}])[0].get('message',{}).get('content'),'usage':data.get('usage')}
    except Exception as e: result={'status':'failed','model':model,'endpoint':endpoint,'error':f'{type(e).__name__}: {e}','note':'Check network, endpoint compatibility, image-input support and credentials.'}
    out=Path(args.out).expanduser().resolve(); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'out':str(out),'model':model,'selected_frame_count':len(used)},ensure_ascii=False,indent=2)); return 0 if result['status']=='ok' else 4

if __name__=='__main__': raise SystemExit(main())
