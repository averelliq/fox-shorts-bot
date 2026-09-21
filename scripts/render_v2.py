"""Fox Shorts V2: original procedural 2D acting and review-only video output.
The narration uses the free, network-dependent edge-tts service; no API key.
It intentionally fails rather than silently substituting a robotic voice.
"""
import argparse
import asyncio
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS = 540, 960, 15
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
VOICE = 'en-US-GuyNeural'
ORANGE, CREAM, INK = '#F18B39', '#FFF0D5', '#22293C'


def command(parts):
    return subprocess.run(parts, text=True, capture_output=True, check=True)


def probe(path):
    return json.loads(command(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]).stdout)


def write_text(d, text, box, size=26, fill='white', max_lines=4):
    x1,y1,x2,y2=box; font=ImageFont.truetype(FONT,size)
    words=text.split(); lines=[]; current=''
    for word in words:
        trial=(current+' '+word).strip()
        if d.textbbox((0,0),trial,font=font)[2]>x2-x1 and current:
            lines.append(current); current=word
        else:current=trial
    if current:lines.append(current)
    if len(lines)>max_lines: raise ValueError('Caption is too long for safe zone: '+text)
    step=size+9; y=(y1+y2-len(lines)*step)//2
    for line in lines:
        d.text(((x1+x2)//2,y),line,font=font,anchor='mt',fill=fill,stroke_width=1,stroke_fill='#192239'); y+=step


def background(d, scene, t):
    themes={'office':('#1A304A','#29455D'),'wifi':('#1B3C4B','#28635F'),'boss':('#382942','#644255'),'rent':('#342A4E','#66516E')}
    color1,color2=themes[scene]
    d.rectangle((0,0,W,H),fill=color1)
    for k in range(0,H,12):
        shade=math.sin(k/130+t/9); d.line((0,k,W,k),fill=color2 if shade>0 else color1,width=6)
    if scene in ('office','wifi','boss'):
        d.rounded_rectangle((22,175,518,610),radius=25,fill='#426079',outline='#7894A6',width=5)
        d.rectangle((55,210,485,555),fill='#98C9D1')
        for x in (110,225,345):d.rectangle((x,365,x+65,555),fill='#5D8A9C')
        d.ellipse((360,232,436,307),fill='#FFE5A5')
        d.rectangle((0,735,W,H),fill='#51424C')
        d.rounded_rectangle((0,700,W,780),radius=12,fill='#98775E')
    else:
        d.rectangle((24,190,516,620),fill='#625174')
        d.rounded_rectangle((50,219,488,573),radius=22,fill='#AC9ABE')
        d.ellipse((98,285,431,610),fill='#F4CE96')
        d.rectangle((0,743,W,H),fill='#59465B')
        d.rounded_rectangle((35,702,505,781),radius=10,fill='#8F6B61')
    d.rounded_rectangle((25,52,515,117),radius=17,fill='#132638')
    write_text(d,'FOX VS ADULTING',(45,63,495,106),23,'#FFDA83',1)


def boss(d,t,emotion='stern'):
    # Secondary actor is deliberately recognizably different from the fox.
    bob=math.sin(t*3)*3; x=405;y=565+bob
    d.ellipse((x-54,y+45,x+64,y+195),fill='#465776')
    d.ellipse((x-54,y-83,x+58,y+64),fill='#BC8A75',outline='#674F54',width=4)
    d.polygon([(x-60,y-32),(x-34,y-100),(x+44,y-89),(x+59,y-30)],fill='#292E41')
    for dx in (-20,21):d.ellipse((x+dx-6,y-11,x+dx+6,y+2),fill=INK)
    d.line((x-25,y+28,x+25,y+25),fill='#563B3D',width=5)
    d.line((x-42,y+85,x-83,y+110+math.sin(t*5)*9),fill='#465776',width=21)
    d.line((x+50,y+85,x+85,y+100-math.sin(t*4)*12),fill='#465776',width=21)


def fox(d,t,action='talk',emotion='smug',x=210,y=573,scale=1.0,speaking=True):
    # All limbs use one shared identity; pose offsets animate whole body, not just mouth.
    sway=math.sin(t*4.0)*5 if action!='walk' else math.sin(t*9)*13
    bob=math.sin(t*(9 if action=='walk' else 4))* (10 if action=='walk' else 4)
    x+=sway; y+=bob
    def p(px,py):return (int(x+(px-250)*scale),int(y+(py-570)*scale))
    def poly(points,fill):d.polygon([p(*pt) for pt in points],fill=fill)
    def oval(bounds,fill,outline=None,width=2):
        q1=p(bounds[0],bounds[1]);q2=p(bounds[2],bounds[3]);d.ellipse((*q1,*q2),fill=fill,outline=outline,width=width)
    tail=math.sin(t*5)*25
    poly([(290,710),(413+tail,621),(462+tail,670),(412+tail,791),(304,805)],'#E47835')
    poly([(437+tail,635),(462+tail,670),(430+tail,718),(393+tail,701)],CREAM)
    leg=math.sin(t*9)*26 if action=='walk' else 0
    d.line((p(207,775),p(192+leg,845)),fill='#A44F32',width=max(8,int(26*scale)))
    d.line((p(302,775),p(316-leg,845)),fill='#A44F32',width=max(8,int(26*scale)))
    oval((176,554,328,796),ORANGE,'#AF5D36',3)
    oval((222,630,281,777),CREAM)
    gesture=38*math.sin(t*6) if action in ('talk','point','show_phone') else 10
    d.line((p(193,632),p(147,694-gesture)),fill=ORANGE,width=max(8,int(25*scale)))
    oval((131,676-gesture,163,709-gesture),'#F6AC66')
    d.line((p(305,628),p(365,680+gesture)),fill=ORANGE,width=max(8,int(24*scale)))
    oval((347,664+gesture,382,697+gesture),'#F6AC66')
    poly([(167,473),(179,335),(246,420)],ORANGE)
    poly([(185,435),(190,360),(226,415)],'#F9B29B')
    poly([(263,410),(342,330),(360,468)],ORANGE)
    poly([(289,415),(337,358),(345,437)],'#F9B29B')
    oval((150,401,352,612),ORANGE,'#9C4C30',4)
    poly([(156,518),(251,563),(349,512),(319,608),(179,606)],CREAM)
    blink=t%3.5<.13
    for ex in (206,295):
        if blink:d.line((p(ex-14,478),p(ex+14,478)),fill=INK,width=4)
        else:
            oval((ex-15,457,ex+14,492),'white')
            oval((ex-4,467,ex+5,487),INK)
    if emotion in ('surprised','worried'):
        d.arc((*p(181,440),*p(226,460)),180,360,fill=INK,width=4)
        d.arc((*p(273,440),*p(316,460)),180,360,fill=INK,width=4)
    oval((239,539,266,558),INK)
    if emotion=='surprised' or (speaking and math.sin(t*16)>.0):oval((234,565,273,599),'#672C46')
    else:d.arc((*p(227,559),*p(283,593)),0,180,fill='#673748',width=4)
    if action=='show_phone':
        # Phone follows moving hand; visible interaction is different from generic talking.
        cx,cy=p(367,645+gesture)
        d.rounded_rectangle((cx-35,cy-52,cx+35,cy+55),radius=8,fill='#182C41',outline='#E5D4A2',width=4)
        d.rounded_rectangle((cx-25,cy-39,cx+25,cy+38),radius=3,fill='#7ED8D4')
        d.arc((cx-10,cy-15,cx+10,cy+5),190,350,fill='#18394A',width=3)


def prop(d,scene,t):
    if scene=='office':
        d.rounded_rectangle((45,620,175,710),radius=8,fill='#17283C',outline='#C2D1D7',width=4)
        write_text(d,'PAY: $0',(51,635,169,686),17,'#FFDD9D',1)
        d.rounded_rectangle((280,690,480,734),radius=8,fill='#F7E0A9')
        write_text(d,'EXPOSURE',(290,689,470,729),18,INK,1)
    elif scene=='wifi':
        d.rounded_rectangle((40,215,500,370),radius=15,fill='#F0E6C6',outline='#274956',width=5)
        write_text(d,'OFFICE WI-FI',(60,228,480,288),28,INK,1)
        write_text(d,'Password: EXPOSED',(62,286,478,356),20,'#274956',1)
        for j in range(5):
            xx=53+j*95; yy=520+math.sin(t*3+j)*7
            d.ellipse((xx,yy,xx+46,yy+46),fill='#F9D38B')
            d.line((xx+23,yy+46,xx+23,yy+95),fill='#415D70',width=18)
    elif scene=='boss':
        d.rounded_rectangle((45,210,490,310),radius=18,fill='#FCDFB1')
        write_text(d,'YOU ARE FIRED!',(58,225,477,288),30,'#552F38',1)
        d.polygon([(110,352),(140,385),(130,402),(165,420),(108,411),(102,379)],fill='#FFD768')
    elif scene=='rent':
        d.rounded_rectangle((308,350,506,560),radius=8,fill='#F5EAD5',outline='#3A3452',width=4)
        write_text(d,'RENT DUE\n$1,200',(316,369,498,520),25,'#47374C',3)
        d.ellipse((380,580,476,696),fill='#C3A4A8',outline='#57465F',width=4)
        d.ellipse((397,605,412,623),fill=INK)
        d.ellipse((440,605,455,623),fill=INK)
        d.line((408,651,452,651),fill=INK,width=4)


def make_frame(t,seg,voice_length):
    scene=seg['scene']; emotion=seg.get('emotion','smug'); action=seg.get('action','talk')
    image=Image.new('RGB',(W,H),'#17283C'); d=ImageDraw.Draw(image)
    background(d,scene,t)
    if scene=='boss':boss(d,t)
    prop(d,scene,t)
    # Simple tracked camera change for each story beat, with occasional walking.
    fx={'office':(215,575),'wifi':(184+math.sin(t*2)*15,578),'boss':(158,582),'rent':(175+math.sin(t*2)*10,580)}[scene]
    fox(d,t,action,emotion,*fx,scale=.84 if scene=='boss' else 1,speaking=t<voice_length-.14)
    d.rounded_rectangle((15,801,525,925),radius=19,fill='#111C2D',outline='#4C6175',width=2)
    write_text(d,seg['text'],(36,813,504,916),25,'white',3)
    return image


async def synth(text,path):
    await edge_tts.Communicate(text,VOICE,rate='+6%').save(str(path))
    if path.stat().st_size<2000:raise RuntimeError('English TTS audio missing or too short')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--story',default=str(ROOT/'stories/episode.json'))
    parser.add_argument('--out',default=str(ROOT/'output/short.mp4'))
    parser.add_argument('--max-seconds',type=float,default=58)
    args=parser.parse_args()
    data=json.loads(Path(args.story).read_text(encoding='utf-8'))
    scenes=data['segments']
    assert len(scenes)>=4, 'Need at least four distinct story beats'
    assert len(set(s['scene'] for s in scenes))>=3, 'Need three different settings'
    assert all(s['scene'] in {'office','wifi','boss','rent'} for s in scenes)
    assert all(s.get('text','').strip() for s in scenes)
    assert shutil.which('ffmpeg') and shutil.which('ffprobe'), 'Install ffmpeg and ffprobe'
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    checks=[]; lengths=[]
    with tempfile.TemporaryDirectory() as temp:
        tmp=Path(temp); clips=[]
        for idx,seg in enumerate(scenes):
            audio=tmp/f'voice{idx}.mp3'
            try:asyncio.run(synth(seg['text'],audio))
            except Exception as exc:raise RuntimeError('Natural voice failed; no robotic fallback. Retry later: '+str(exc)) from exc
            voice_len=float(probe(audio)['format']['duration'])
            length=voice_len+.16;lengths.append(length)
            raw=tmp/f'frames{idx}.rgb'; frames=math.ceil(length*FPS)
            a=make_frame(.3,seg,voice_len);b=make_frame(min(voice_len*.65,2.1),seg,voice_len)
            movement=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
            checks.append(round(movement,2))
            assert movement>1.3, f'Static scene {idx}: {movement}'
            with raw.open('wb') as stream:
                for n in range(frames):stream.write(make_frame(n/FPS,seg,voice_len).tobytes())
            clip=tmp/f'clip{idx}.mp4'
            command(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i',str(raw),'-i',str(audio),'-filter_complex','[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];[1:a]apad[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','23','-r','30','-c:a','aac','-b:a','160k','-t',str(length),'-movflags','+faststart',str(clip)])
            clips.append(clip)
        concat=tmp/'concat.txt';concat.write_text(''.join(f"file '{clip}'\n" for clip in clips))
        command(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(out)])
    info=probe(out); v=next(s for s in info['streams'] if s['codec_type']=='video')
    audio_streams=[s for s in info['streams'] if s['codec_type']=='audio']
    duration=float(info['format']['duration'])
    assert (v['width'],v['height'])==(1080,1920)
    assert audio_streams and duration>8 and duration<=args.max_seconds,(duration,audio_streams)
    report={'title':data['title'],'description':data['description'],'duration_seconds':round(duration,2),'width':1080,'height':1920,'voice':VOICE,'animated_scenes':len(scenes),'scene_motion_scores':checks,'technical_qc':'passed','human_review_required':True,'youtube_uploaded':False}
    (out.parent/'metadata.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('V2 PASS:',json.dumps(report))

if __name__=='__main__': main()
