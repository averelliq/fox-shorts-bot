"""Rusty V6: review-only illustrated scene proof using approved V5 sprite art.
Redesigned backgrounds, restricted sprite enlargement, eased scene acting.
Still NOT full hand-drawn animation or restored high-resolution source art.
"""
import asyncio
import base64
import hashlib
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
W,H,FPS=540,960,12
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def run(args):
    p=subprocess.run(args, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f'{args[0]} exited {p.returncode}: {p.stderr[-1400:]}')
    return p.stdout


def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))


def art():
    folder=ROOT/'assets'
    spec=json.loads((folder/'rusty_atlas.json').read_text())
    path=folder/'rusty_atlas.png'
    if not path.exists():
        parts=[(folder/f'v5_atlas_part_{i}.txt').read_text().strip() for i in range(4)]
        path.write_bytes(base64.b64decode(''.join(parts),validate=True))
    if hashlib.sha256(path.read_bytes()).hexdigest()!=spec['sha256']:
        raise RuntimeError('Approved-art checksum failed')
    atlas=Image.open(path).convert('RGBA')
    return {name:atlas.crop((x,y,x+w,y+h)) for name,(x,y,w,h) in spec['sprites'].items()},spec


def smooth(t):
    t=max(0.0,min(1.0,t))
    return t*t*(3-2*t)


def bg(kind):
    im=Image.new('RGBA',(W,H),'#F5E8DB')
    d=ImageDraw.Draw(im)
    if kind=='office':
        d.rectangle((0,0,W,670),fill='#FBEBD9')
        d.rectangle((0,670,W,H),fill='#DDC1AB')
        d.rounded_rectangle((35,120,505,468),radius=18,fill='#D7EBEE',outline='#5C7380',width=5)
        d.rectangle((262,120,275,468),fill='#7899A4')
        d.rectangle((35,289,505,300),fill='#7899A4')
        for i,x in enumerate(range(55,490,68)):
            d.rectangle((x,468-(62+i*23)%140,x+43,468),fill='#A2BEC7')
        d.rounded_rectangle((14,543,528,645),radius=15,fill='#B98E70',outline='#5A4C52',width=5)
        d.rectangle((52,645,76,858),fill='#806357')
        d.rectangle((465,645,489,858),fill='#806357')
        d.rounded_rectangle((332,414,465,542),radius=9,fill='#475763',outline='#353D4A',width=4)
        d.rounded_rectangle((342,425,455,503),radius=4,fill='#A4D7D3')
        d.rectangle((391,542,402,561),fill='#475763')
        d.rounded_rectangle((424,531,461,575),radius=5,fill='#EBD39C',outline='#6A5656',width=3)
        d.rounded_rectangle((391,181,489,250),radius=9,fill='#F6DDA3',outline='#88746B',width=3)
        d.text((407,201),'WI-FI',font=ImageFont.truetype(FONT,17),fill='#46404C')
        for i in range(11):
            xx=19+i*47
            d.arc((xx,50,xx+21,69),190,335,fill='#E9D3C2',width=2)
    else:
        d.rectangle((0,0,W,680),fill='#F5E4D8')
        d.rectangle((0,680,W,H),fill='#DBC2B2')
        d.polygon([(0,80),(100,40),(100,688),(0,753)],fill='#E8D7CA')
        d.polygon([(540,80),(439,40),(439,688),(540,753)],fill='#E8D7CA')
        d.rounded_rectangle((143,111,399,678),radius=18,fill='#F8EFE6',outline='#BAA296',width=4)
        d.rounded_rectangle((300,170,387,654),radius=9,fill='#BC8472',outline='#6D5660',width=5)
        d.ellipse((363,401,376,414),fill='#FBE0A0',outline='#6D5660',width=2)
        d.rounded_rectangle((159,253,269,381),radius=8,fill='#BED8D7',outline='#6F8B8E',width=3)
        d.rectangle((169,265,258,372),fill='#DAE9E6')
        d.rounded_rectangle((70,535,128,688),radius=10,fill='#9E715F',outline='#694D52',width=3)
        for i in range(9):
            x=-180+i*110
            d.line((x,682,x+230,960),fill='#C9B5A8',width=2)
    return im


def sprite_on(frame, sprite, cx, foot, factor, angle=0):
    # Cap magnification: upscaling cannot recreate detail lost in original art.
    factor=min(factor,2.28)
    w=max(1,int(sprite.width*factor));h=max(1,int(sprite.height*factor))
    sp=sprite.resize((w,h),Image.Resampling.LANCZOS)
    if angle:
        sp=sp.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    x=int(cx-sp.width/2);y=int(foot-sp.height)
    if x < 12: x=12
    if x+sp.width>W-12:x=W-12-sp.width
    alpha=sp.getchannel('A')
    shadow=Image.new('RGBA',sp.size,(43,30,33,0))
    shadow.putalpha(alpha.point(lambda q:int(q*.23)))
    shadow=shadow.filter(ImageFilter.GaussianBlur(5))
    frame.alpha_composite(shadow,(x+4,y+6))
    frame.alpha_composite(sp,(x,y))


def caption(frame,text):
    d=ImageDraw.Draw(frame)
    font=ImageFont.truetype(FONT,25)
    words=text.split(); lines=[];line=''
    for word in words:
        attempt=(line+' '+word).strip()
        if d.textbbox((0,0),attempt,font=font)[2]<W-96:line=attempt
        else: lines.append(line);line=word
    if line: lines.append(line)
    if not lines: return
    dy=39; height=dy*len(lines)+22
    y=H-105-height
    d.rounded_rectangle((25,y,W-25,y+height),radius=18,fill='#293940',outline='#91ABA4',width=2)
    for i,ln in enumerate(lines):
        box=d.textbbox((0,0),ln,font=font)
        d.text(((W-(box[2]-box[0]))/2,y+9+i*dy),ln,font=font,fill='#FFF3D9')


def frame_at(index,duration,sprites,backdrops):
    t=index/FPS
    p=t/duration
    if p<.28: beat='shock';q=smooth(p/.28)
    elif p<.60:beat='phone';q=smooth((p-.28)/.32)
    elif p<.81:beat='share';q=smooth((p-.60)/.21)
    else:beat='walk';q=smooth((p-.81)/.19)
    canvas=backdrops['office' if beat!='walk' else 'hall'].copy()
    d=ImageDraw.Draw(canvas)
    if beat=='shock':
        d.rounded_rectangle((56,368,276,428),radius=12,fill='#FFF4C9',outline='#946E67',width=3)
        d.text((77,388),'EXPOSURE?!',font=ImageFont.truetype(FONT,22),fill='#B66C57')
        sprite_on(canvas,sprites['shocked'],259-11*q,760+5*math.sin(t*7),2.14,angle=-5+3*q)
        text='My boss paid me in exposure.'
    elif beat=='phone':
        d.rounded_rectangle((354,355,495,469),radius=12,fill='#FFF1B5',outline='#7F6B65',width=3)
        d.text((371,383),'WI-FI',font=ImageFont.truetype(FONT,26),fill='#455158')
        d.text((370,418),'••••••',font=ImageFont.truetype(FONT,22),fill='#455158')
        d.ellipse((426,475,440,489),fill='#FFF7D5',outline='#CF9870',width=2)
        sprite_on(canvas,sprites['phone'],251+14*q,772+3*math.sin(t*5),2.13,angle=1.5*math.sin(t*4))
        text='So I found his Wi-Fi password.'
    elif beat=='share':
        d.rounded_rectangle((334,363,493,486),radius=11,fill='#FFECC2',outline='#816762',width=3)
        d.text((357,392),'FREE',font=ImageFont.truetype(FONT,27),fill='#46545B')
        d.text((347,428),'WI-FI!',font=ImageFont.truetype(FONT,25),fill='#46545B')
        for x,c in [(365,'#B7B1C4'),(410,'#D7B6A7'),(455,'#AFBFC2')]:
            d.ellipse((x-15,542,x+15,572),fill=c,outline='#6B6471',width=2)
            d.line((x,573,x,635),fill='#6B6471',width=7)
        sprite_on(canvas,sprites['phone'],238+14*q,776,2.11,angle=-2+3*math.sin(t*4))
        text='I shared it with everyone.'
    else:
        # Only one walking illustration is available; do not mislabel this a walk cycle.
        x=133+256*q
        sprite_on(canvas,sprites['walk'],x,770+3*math.sin(t*9),2.03)
        for n in range(3):
            px=x-74-31*n
            d.line((px,773,px+17,773),fill='#B79A8D',width=2)
        text='Now who is paying the rent?'
    caption(canvas,text)
    return canvas.convert('RGB'),beat


async def neural(text,path):
    import edge_tts
    await edge_tts.Communicate(text,'en-US-GuyNeural',rate='+12%').save(str(path))


def main():
    sprites,spec=art()
    backgrounds={'office':bg('office'),'hall':bg('hall')}
    spoken='My boss paid me in exposure. So I found his Wi-Fi password. I shared it with everyone. Now who is paying the rent?'
    out=ROOT/'output';out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        tmp=Path(temp);audio=tmp/'voice.mp3'
        offline=os.getenv('FOX_OFFLINE_TEST')=='1'
        if offline:
            run(['espeak','-v','en-us','-s','195','-w',str(tmp/'voice.wav'),spoken]);audio=tmp/'voice.wav'
        else:
            try:asyncio.run(neural(spoken,audio))
            except Exception as e:raise RuntimeError('Neural voice unavailable; do not substitute a robotic publishing voice') from e
        speech_length=float(probe(audio)['format']['duration'])
        duration=max(5.5,speech_length+.15)
        if duration>15:raise RuntimeError('Unexpectedly long speech; inspect voice timing')
        raw=tmp/'frames.rgb'; n=math.ceil(duration*FPS);changes=[]
        with raw.open('wb') as fh:
            for i in range(n):
                im,beat=frame_at(i,duration,sprites,backgrounds)
                if not changes or changes[-1][1]!=beat:changes.append((round(i/FPS,2),beat))
                fh.write(im.tobytes())
        video=out/'short_v6_proof.mp4'
        run(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r',str(FPS),'-i',str(raw),'-i',str(audio),'-filter_complex','[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];[1:a]apad[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','19','-r','30','-c:a','aac','-b:a','160k','-t',str(duration),'-movflags','+faststart',str(video)])
    data=probe(video);v=next(s for s in data['streams'] if s['codec_type']=='video');a=next((s for s in data['streams'] if s['codec_type']=='audio'),None)
    seconds=float(data['format']['duration'])
    assert a and (v['width'],v['height'])==(1080,1920) and 5<=seconds<=15 and len(changes)==4
    metadata={'version':'V6 asset-reuse background proof','technical_qc':'passed','duration_seconds':round(seconds,2),'scenes':changes,'character_art_sha256':spec['sha256'],'source_atlas_pixels':spec['dimensions'],'upscale_does_not_restore_original_detail':True,'real_walk_cycle':False,'human_voice_reviewed':False,'youtube_uploaded':False,'voice_engine':'eSpeak offline technical test' if offline else 'edge-tts'}
    (out/'metadata_v6.json').write_text(json.dumps(metadata,indent=2))
    print('PASS V6',json.dumps(metadata))

if __name__=='__main__':main()