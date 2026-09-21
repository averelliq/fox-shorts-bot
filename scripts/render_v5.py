"""V5 review-only sprite proof. The fox is sampled from APPROVED drawings, not SVG geometry."""
import asyncio,base64,hashlib,json,math,os,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
W,H,FPS=540,960,12
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def cmd(args):
 p=subprocess.run(args,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr[-1600:])
 return p.stdout
def probe(f):return json.loads(cmd(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]))
def sprites():
 root=ROOT/'assets';spec=json.loads((root/'rusty_atlas.json').read_text());f=root/'rusty_atlas.png'
 if not f.exists():
  chunks=[(root/f'v5_atlas_part_{j}.txt').read_text().strip() for j in range(4)]
  f.write_bytes(base64.b64decode(''.join(chunks),validate=True))
 assert hashlib.sha256(f.read_bytes()).hexdigest()==spec['sha256'],'Art transfer checksum mismatch'
 a=Image.open(f).convert('RGBA');assert list(a.size)==spec['dimensions']
 return {n:a.crop((x,y,x+w,y+h)) for n,(x,y,w,h) in spec['sprites'].items()},spec
async def speech(text,f):
 import edge_tts
 await edge_tts.Communicate(text,'en-US-GuyNeural',rate='+16%').save(str(f))
def ease(x):
 x=max(0.,min(1.,x));return x*x*(3-2*x)
def draw_frame(k,duration,assets,story):
 t=k/FPS;p=t/duration;beats=story['beats'];b=0;start=0
 for i,item in enumerate(beats):
  if p<start+item['share'] or i==len(beats)-1:b=i;break
  start+=item['share']
 beat=beats[b];u=(p-start)/beat['share'];pose=beat['pose']
 im=Image.new('RGB',(W,H),'#FFF5E7');d=ImageDraw.Draw(im)
 for y in range(0,H,42):d.line((0,y,W,y),fill='#F5EAE1')
 if beat['location']=='office':
  d.rounded_rectangle((26,145,513,686),radius=28,fill='#E9E1CE',outline='#5B5667',width=5)
  d.rounded_rectangle((54,188,483,483),radius=12,fill='#BFDADB',outline='#6C9295',width=5)
  d.line((267,190,267,478),fill='#6C9295',width=5)
  d.rounded_rectangle((8,693,534,749),radius=15,fill='#B1856D',outline='#5F4A4B',width=4)
  if b==1:
   d.rounded_rectangle((371,297,510,409),radius=12,fill='#FFF0B9',outline='#5B5667',width=4)
   d.text((395,335),'WI-FI',font=ImageFont.truetype(FONT,21),fill='#333A44')
 else:
  d.rectangle((0,721,W,H),fill='#EAD9CB')
  d.rounded_rectangle((280,177,506,719),radius=14,fill='#C79887',outline='#5D4657',width=6)
  d.ellipse((461,471,474,484),fill='#FFDEA4',outline='#433745',width=2)
 art=assets[pose]
 if b==0:scale=2.85+.35*ease(u);x=265;y=665+5*math.sin(t*8)
 elif b==1:scale=2.55;x=230+48*ease(u);y=689+4*math.sin(t*6)
 else:scale=2.6;x=76+345*ease(u);y=698+7*math.sin(t*13)
 out=art.resize((int(art.width*scale),int(art.height*scale)),Image.Resampling.LANCZOS)
 im.paste(out,(int(x-out.width/2),int(y-out.height)),out)
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((28,802,513,904),radius=23,fill='#293B41',outline='#71938D',width=3)
 f=ImageFont.truetype(FONT,27);caption=beat['caption'];bb=d.textbbox((0,0),caption,font=f)
 d.text(((W-(bb[2]-bb[0]))/2,839),caption,font=f,fill='#FFF4D8')
 return im,pose
def main():
 story=json.loads((ROOT/'stories/proof_v5.json').read_text())
 art,spec=sprites();assert len(story['beats'])==3
 assert {'phone','walk','shocked'}=={b['pose'] for b in story['beats']}
 out=ROOT/'output/short_v5_proof.mp4';out.parent.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory() as folder:
  t=Path(folder);voice=t/'voice.mp3'
  offline=os.getenv('FOX_OFFLINE_TEST')=='1'
  if offline:cmd(['espeak','-v','en-us','-s','185','-w',str(t/'voice.wav'),story['spoken_text']]);voice=t/'voice.wav'
  else:
   try:asyncio.run(speech(story['spoken_text'],voice))
   except Exception as e:raise RuntimeError('Natural TTS unavailable; no robotic publishing fallback') from e
  length=float(probe(voice)['format']['duration'])
  if length>4.9:raise RuntimeError(f'Voice too long for 3-5s acting proof: {length:.2f}s')
  duration=max(3.2,length+.13);n=math.ceil(FPS*duration);poses=[];raw=t/'frames.rgb'
  with raw.open('wb') as stream:
   for k in range(n):
    image,pose=draw_frame(k,duration,art,story)
    if not poses or poses[-1][1]!=pose:poses.append((round(k/FPS,2),pose))
    stream.write(image.tobytes())
  cmd(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r',str(FPS),'-i',str(raw),'-i',str(voice),'-filter_complex','[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];[1:a]apad[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','22','-r','30','-c:a','aac','-b:a','160k','-t',str(duration),'-movflags','+faststart',str(out)])
 meta=probe(out);v=next(z for z in meta['streams'] if z['codec_type']=='video');a=next((z for z in meta['streams'] if z['codec_type']=='audio'),None)
 seconds=float(meta['format']['duration']);assert a and (v['width'],v['height'])==(1080,1920) and 3<=seconds<=5.2 and len(poses)==3
 report={'version':'V5 approved-art sprite proof','technical_qc':'passed','duration_seconds':round(seconds,2),'poses':poses,'art_sha256':spec['sha256'],'audio':'eSpeak offline test (do not publish)' if offline else 'edge-tts neural','actual_character_motion':'pose cuts and screen motion only; no drawn inbetweens','voice_listened_to_by_human':False,'youtube_uploaded':False}
 (out.parent/'metadata_v5.json').write_text(json.dumps(report,indent=2))
 print(f'PASS V5: {seconds:.2f}s | 1080x1920 | audio | {len(poses)} pre-drawn poses | review-only')
if __name__=='__main__':main()
