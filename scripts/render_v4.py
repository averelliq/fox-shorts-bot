"""V4 hand-inked cartoon renderer. Public-source readable version.
This entrypoint supports V4 review without YouTube publication.
"""
import asyncio, io, json, math, os, shutil, subprocess, tempfile, wave
from pathlib import Path
import cairosvg, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

ROOT=Path(__file__).resolve().parents[1]
W,H,FPS=540,960,12
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
INK='#322C39'; PAPER='#FFF8ED'; ORANGE='#E98243'; CREAM='#FFE8C2'; TEAL='#268875'
VOICES={'fox':'en-US-GuyNeural','boss':'en-US-AndrewNeural','landlord':'en-US-JennyNeural'}

def cmd(args):
    result=subprocess.run(args,capture_output=True,text=True)
    if result.returncode:raise RuntimeError(f'Command failed: {args}\n{result.stderr[-3000:]}')
    return result

def probe(path):
    return json.loads(cmd(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]).stdout)

def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def path(d,fill='none',stroke=INK,width=4):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'

def box(x,y,w,h,fill='none',r=0,stroke=INK,sw=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def oval(cx,cy,rx,ry,fill,stroke=INK,sw=3):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def room(scene,t):
    s=[box(0,0,W,H,PAPER,0,'none',0),path('M 8 726 Q 270 708 535 731','none','#BEA7A3',3)]
    if scene in ('offer','idea','wifi','fired','retort'):
        s += [box(27,134,485,454,'#FBEDE3',23,'#C49FA0',4),box(65,185,406,310,'#C7E2E5',8,'#739A9D',4),path('M 254 185 V 496 M 66 335 H 472','none','#7BABA9',3),oval(413,244,28,28,'#FFF4B9','none',0),box(9,701,525,57,'#BD8E76',8)]
    else:
        s += [box(70,109,410,604,'#E9D7DA',8,'#816D80',5),box(117,158,298,536,'#C7958B',5,'#6A5366',5),oval(383,428,9,9,'#FFE2A9')]
    for x in (25,117,209,301,393):s.append(path(f'M {x} 917 q 17 -10 31 0','none','#DDC7BE',2))
    return ''.join(s)

def fox(x,y,scale=1,pose='grin',t=0,speaking=True):
    walk=pose=='walk'; stride=math.sin(t*10)*(24 if walk else 2)
    bob=math.sin(t*(10 if walk else 3))*(9 if walk else 3)
    head={'shock':-14,'phone':9,'point':-8,'grin':10,'plead':-17}.get(pose,0)+math.sin(t*2)*2
    tail=math.sin(t*3.4)*18
    s=[f'<g transform="translate({x:.2f} {y+bob:.2f}) scale({scale:.3f})">',
       path(f'M 40 73 Q {165+tail:.0f} -37 {168+tail:.0f} 77 Q {140+tail:.0f} 182 50 144 Z',ORANGE,INK,5),
       path(f'M {143+tail:.0f} 49 Q {171+tail:.0f} 57 {168+tail:.0f} 77 Q {163+tail:.0f} 112 {128+tail:.0f} 133 L 118 119 Z',CREAM,INK,3),
       path(f'M -23 132 L {-50+stride:.0f} 181','none',INK,17),path(f'M 24 132 L {49-stride:.0f} 179','none',INK,17),
       oval(-53+stride,182,31,13,'#41445E'),oval(47-stride,181,31,13,'#41445E'),
       path('M -53 15 Q 0 -5 47 18 L 58 127 Q 14 160 -49 128 Z',TEAL,INK,5),
       path('M -46 21 L -13 49 L 0 25 L 15 49 L 46 22','none','#A7DCC5',5),
       path('M -10 45 Q -6 100 -15 143','none','#145F60',3),oval(17,83,5,5,'#FFDE91'),oval(18,111,5,5,'#FFDE91'),
       path('M -36 95 q 16 -6 28 0 l -3 29 l -23 0 Z','#3EA38D',INK,2)]
    if pose=='phone':
        s += [path('M -40 28 Q -88 27 -76 87','none',ORANGE,19),oval(-76,88,13,13,CREAM),
              path('M 46 28 Q 78 -14 89 -35','none',ORANGE,19),oval(89,-35,14,12,CREAM),
              box(66,-110,73,120,'#303348',11,'#272737',4),box(75,-96,55,91,'#B4EFE9',4,'none',0),
              oval(102,-60,11,11,'#FFF1B2'),path('M 94 -62 l 7 6 l 11 -15','none','#256A6A',3),
              path(f'M 90 -39 Q {123+math.sin(t*15)*5:.0f} -32 104 -18','none',CREAM,9)]
    else:
        arm={'point':-42,'plead':-8,'shock':20}.get(pose,0)
        s += [path(f'M -39 27 Q -84 44 {-90+arm:.0f} {92+arm/3:.0f}','none',ORANGE,19),oval(-90+arm,92+arm/3,13,12,CREAM),
              path(f'M 43 27 Q 88 {39+arm/2:.0f} {95-arm/3:.0f} {72+arm:.0f}','none',ORANGE,19),oval(95-arm/3,72+arm,13,12,CREAM)]
    s += [f'<g transform="rotate({head:.2f} 0 -86)">',
          path('M -80 -146 L -103 -254 Q -70 -252 -28 -195 L 22 -204 Q 62 -260 90 -245 L 72 -131 Z',ORANGE,INK,6),
          path('M -81 -229 L -70 -177 L -41 -187 Z','#F6B4A8',INK,2),path('M 51 -187 L 75 -230 L 66 -174 Z','#F6B4A8',INK,2),
          path('M -89 -153 Q -91 -202 -49 -205 L -26 -221 L -13 -205 Q 15 -232 35 -205 Q 76 -205 87 -159 Q 103 -98 73 -61 Q 56 -22 1 -15 Q -65 -23 -90 -84 Z',ORANGE,INK,6),
          path('M -90 -145 Q -68 -191 -20 -191 Q -2 -220 24 -189 Q 69 -190 82 -148 Q 39 -166 21 -144 Q -17 -163 -32 -138 Q -59 -153 -90 -145 Z','#C06C46',INK,2),
          path('M -86 -94 Q -58 -78 -34 -50 L -1 -45 Q 34 -69 84 -92 Q 69 -31 25 -18 L -2 -32 Q -34 -16 -63 -47 Z',CREAM,INK,4),
          oval(-37,-111,23,31,'white'),oval(37,-111,23,31,'white'),oval(-35,-105,8,15,INK,'none',0),oval(38,-105,8,15,INK,'none',0),
          path('M -67 -148 Q -47 -162 -22 -144 M 19 -147 Q 43 -164 62 -148','none',INK,5),
          path('M -19 -70 Q 2 -88 22 -70 Q 18 -54 -3 -51 Z',INK,INK,2)]
    if speaking and math.sin(t*13)>-.2:s.append(path('M -24 -45 Q 2 -18 27 -43 Q 13 13 -9 -8 Q -29 -19 -24 -45 Z','#652F46',INK,4))
    elif pose in ('shock','plead'):s.append(oval(3,-38,13,17,'#652F46'))
    else:s.append(path('M -27 -40 Q 0 -15 27 -42','none',INK,4))
    return ''.join(s)+'</g></g>'

def boss(x,y,scale=1,t=0,speaking=False,angry=False):
    a=math.sin(t*10)*5
    s=[f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.2f})">',
       path('M -57 36 Q -78 133 -45 169 L 58 169 Q 87 108 50 32 Z','#425B80',INK,5),
       path('M -55 72 Q -103 61 -101 -3','none','#425B80',20),path(f'M 51 68 Q 95 55 {106+a:.0f} -5','none','#425B80',20),
       path('M -64 -110 Q -108 -147 -87 -177 L -29 -151 Q 0 -167 30 -146 L 85 -179 Q 110 -142 60 -106 L 67 -34 Q 25 23 -59 -32 Z','#B6A8AD',INK,6),
       oval(-48,-98,23,27,'#DDD5D8'),oval(43,-97,23,27,'#DDD5D8'),oval(-46,-96,6,10,INK,'none',0),oval(44,-96,6,10,INK,'none',0),
       path('M -72 -136 L -25 -116 M 21 -118 L 65 -140','none',INK,7)]
    if speaking and math.sin(t*13)>-.1:s.append(oval(0,-20,19,23,'#6F374B'))
    elif angry:s.append(path('M -24 -10 Q 0 -34 27 -8','none',INK,5))
    else:s.append(path('M -17 -14 Q 0 -5 22 -14','none',INK,4))
    return ''.join(s)+'</g>'

def landlord(x,y,scale=1,t=0,shock=False):
    s=[f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.2f})">',
       path('M -54 46 Q -81 114 -53 170 L 62 170 Q 80 111 44 46 Z','#A88BB9',INK,5),
       path('M -47 -114 L -83 -194 Q -43 -184 -27 -146 L 21 -145 Q 45 -184 84 -199 L 56 -107 Z','#DBCDD9',INK,5),
       path('M -53 -109 Q 0 -167 57 -103 L 70 -39 Q 56 20 -2 25 Q -59 15 -69 -51 Z','#DBCDD9',INK,5),
       oval(-26,-64,16,22,'white'),oval(33,-65,16,22,'white'),oval(-24,-62,5,10,INK,'none',0),oval(33,-62,5,10,INK,'none',0),
       oval(2,-26,27,19,'#EEE2E3')]
    if shock:s += [oval(2,4,14,19,'#733952'),path('M -55 77 Q -113 21 -126 -12','none','#A88BB9',18)]
    else:s += [path('M -10 3 Q 1 -1 12 4','none',INK,4)]
    return ''.join(s)+'</g>'

def shot_frame(t,scene,duration,speaker,shot):
    p=t/max(.1,duration);s=[room(scene,t)]
    if scene=='offer':
        s += [boss(405,480,.82,t,speaker=='boss'),fox(165-15*ease(p),520,.87,'shock',t,speaker=='fox'),box(297-70*ease(p),484,94,56,'#F5DFA5',3)]
        s.append(path('M 300 485 l 44 31 l 48 -31','none','#AB8269',3))
    elif scene=='idea':
        s += [fox(255,545,1.34,'phone',t,True),oval(365+10*math.sin(t*7),409+8*math.sin(t*13),8,8,'#FFF8D1')]
    elif scene=='wifi':
        s += [box(300,234,198,210,'#FFEAB1',8),fox(140+40*ease(p),538,.82,'point',t,True),
              oval(350,536,18,23,'#D0A3A3'),oval(405,530,20,22,'#B9BBD3'),oval(455,542,16,21,'#DAB68D')]
        for xx in (350,410,458):s.append(path(f'M {xx} 566 q -20 26 -16 56','none','#648D8D',14))
    elif scene=='fired':
        s += [boss(313+24*ease(p),544-20*ease(p),1.38,t,True,True),fox(84-8*ease(p),627,.48,'shock',t,False)]
    elif scene=='retort':s += [fox(262,580,1.63,'grin',t,True)]
    elif scene=='rent':s += [fox(153,566,.76,'plead',t,speaker=='fox'),landlord(404,543,.83,t,True),box(225,450,92,74,'#FFF6D6',4)]
    elif scene=='door':
        s += [fox(157-28*ease(p),553,.89,'plead',t,True),landlord(375,524,.92,t,True)]
        a=ease((p-.72)/.24)
        if a>0:s += [box(290-330*a,140,248,565,'#BA8174',4),oval(482-330*a,449,9,10,'#F7D98A')]
    else:raise ValueError('Unknown V4 shot '+scene)
    return '<svg xmlns="http://www.w3.org/2000/svg" width="540" height="960" viewBox="0 0 540 960">'+''.join(s)+'</svg>'

def timed_caption(d,text,t,duration):
    words=text.replace('!',' !').replace('?',' ?').split();groups=[];chunk=[]
    for word in words:
        if len(chunk)>=3 or (chunk and sum(map(len,chunk))+len(word)>19):groups.append(' '.join(chunk));chunk=[]
        chunk.append(word)
    if chunk:groups.append(' '.join(chunk))
    weights=[max(1,sum(map(len,g.split()))) for g in groups]
    current=groups[-1];acc=0;pos=min(.999,t/max(.01,duration))*sum(weights)
    for group,w in zip(groups,weights):
        acc+=w
        if pos<acc:current=group;break
    current=current.replace(' !','!').replace(' ?','?')
    font=ImageFont.truetype(FONT,34);bb=d.textbbox((0,0),current,font=font,stroke_width=3);cw=bb[2]-bb[0]
    if cw>490:font=ImageFont.truetype(FONT,28);bb=d.textbbox((0,0),current,font=font,stroke_width=3);cw=bb[2]-bb[0]
    d.rounded_rectangle((max(15,W//2-cw//2-18),787,min(525,W//2+cw//2+18),859),radius=16,fill='#282638',outline='#FFF5DD',width=2)
    d.text((W//2,815),current,anchor='mt',font=font,fill='#FFFDF6',stroke_width=2,stroke_fill='#292638')
    return len(groups)

def raster(t,segment,duration):
    svg=shot_frame(t,segment['scene'],duration,segment['speaker'],segment['shot'])
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=W,output_height=H))).convert('RGB')
    d=ImageDraw.Draw(image);scene=segment['scene']
    if scene=='wifi':
        d.text((399,285),'FREE WI-FI',font=ImageFont.truetype(FONT,22),anchor='mt',fill=INK)
        d.text((399,340),'FOX-EXPOSED',font=ImageFont.truetype(FONT,15),anchor='mt',fill='#66504D')
    elif scene=='fired':d.text((270,132),"YOU'RE FIRED!",font=ImageFont.truetype(FONT,31),anchor='mt',fill='#A64547')
    elif scene=='rent':d.text((271,465),'RENT',font=ImageFont.truetype(FONT,18),anchor='mt',fill=INK)
    elif scene=='offer':d.text((320,502),'$0',font=ImageFont.truetype(FONT,25),anchor='mt',fill='#66483F')
    timed_caption(d,segment['text'],t,duration)
    return image

async def neural_voice(text,path,voice):
    import edge_tts
    await edge_tts.Communicate(text,voice,rate='+8%').save(str(path))
    if path.stat().st_size<2000:raise RuntimeError('English neural narration is empty')

def synth(text,path,speaker):
    if os.getenv('FOX_OFFLINE_TEST')=='1':
        binary=shutil.which('espeak-ng') or shutil.which('espeak')
        if not binary:raise RuntimeError('Offline smoke test needs eSpeak')
        wav=path.with_suffix('.wav');cmd([binary,'-v','en-us','-s','178','-w',str(wav),text])
        cmd(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-c:a','libmp3lame','-q:a','3',str(path)])
        return 'OFFLINE TEST eSpeak (not production)'
    try:asyncio.run(neural_voice(text,path,VOICES[speaker]))
    except Exception as exc:raise RuntimeError('Neural service failed. Refusing robotic production fallback: '+str(exc)) from exc
    return VOICES[speaker]

def trim_voice(path):
    dst=path.with_name(path.stem+'.trim.mp3')
    filt=('silenceremove=start_periods=1:start_duration=0:start_threshold=-38dB:start_silence=0.04,'
          'areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-38dB:start_silence=0.04,areverse')
    cmd(['ffmpeg','-y','-loglevel','error','-i',str(path),'-af',filt,'-c:a','libmp3lame','-q:a','3',str(dst)])
    if dst.stat().st_size<1000:raise RuntimeError('Voice trim created an empty clip')
    dst.replace(path)

def sound_effect(path):
    sr=44100;t=np.arange(int(sr*.35))/sr
    wave_data=np.sin(2*np.pi*(155*t-75*t*t))*np.exp(-16*t)+.35*np.sin(2*np.pi*870*t)*np.exp(-38*t)
    raw=np.clip(wave_data*.13*32767,-32768,32767).astype('<i2')
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(sr);out.writeframes(raw.tobytes())

def main():
    data=json.loads((ROOT/'stories/episode_v4.json').read_text(encoding='utf-8'))
    segments=data['segments'];assert len(segments)>=6 and len({s['scene'] for s in segments})>=5
    assert all(s['speaker'] in VOICES and s['text'].strip() for s in segments)
    for tool in ('ffmpeg','ffprobe'):
        if not shutil.which(tool):raise RuntimeError('Missing '+tool)
    out=ROOT/'output/short.mp4';out.parent.mkdir(parents=True,exist_ok=True)
    motions=[];voice_types=[];durations=[];groups=[]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp=Path(tmpdir);fx=tmp/'foley.wav';sound_effect(fx);clips=[]
        for idx,seg in enumerate(segments):
            voice=tmp/f'voice-{idx}.mp3';voice_types.append(synth(seg['text'],voice,seg['speaker']));trim_voice(voice)
            voice_dur=float(probe(voice)['format']['duration']);length=voice_dur+(.27 if idx==len(segments)-1 else .12)
            durations.append(length);raw=tmp/f'frames-{idx}.rgb';nframes=math.ceil(length*FPS)
            a=raster(.08,seg,voice_dur);b=raster(min(.92*voice_dur,1.8),seg,voice_dur)
            motion=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
            assert motion>1.1,f'Scene {idx} is static: {motion:.2f}'
            motions.append(round(motion,2));groups.append(timed_caption(ImageDraw.Draw(Image.new('RGB',(W,H))),seg['text'],0,voice_dur))
            with raw.open('wb') as fh:
                for n in range(nframes):fh.write(raster(n/FPS,seg,voice_dur).tobytes())
            clip=tmp/f'clip-{idx}.mp4';inputs=['-i',str(voice)];audio='[1:a]apad[a]'
            if idx in (1,2,3,6):
                inputs += ['-i',str(fx)];audio='[1:a]volume=1[a0];[2:a]volume=0.23,adelay=170|170[a1];[a0][a1]amix=inputs=2:duration=longest:dropout_transition=0,apad[a]'
            graph='[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];'+audio
            cmd(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i',str(raw),*inputs,'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','21','-r','30','-c:a','aac','-b:a','160k','-t',str(length),'-movflags','+faststart',str(clip)])
            clips.append(clip)
        manifest=tmp/'concat.txt';manifest.write_text(''.join(f"file '{p}'\n" for p in clips))
        cmd(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(manifest),'-c','copy','-movflags','+faststart',str(out)])
    info=probe(out);video=next(s for s in info['streams'] if s['codec_type']=='video');audio=next((s for s in info['streams'] if s['codec_type']=='audio'),None)
    duration=float(info['format']['duration']);assert audio and (video['width'],video['height'])==(1080,1920) and 3<duration<58
    meta={'title':data['title'],'description':data['description'],'version':'V4-hand-inked','duration_seconds':round(duration,2),'width':1080,'height':1920,'scenes':len(segments),'shot_types':sorted(set(s['shot'] for s in segments)),'motion_scores':motions,'caption_groups':groups,'voice_types':sorted(set(voice_types)),'original_generated_sfx':True,'youtube_uploaded':False,'human_artistic_review_required':True,'technical_qc':'passed','voice_human_listening_verified':False}
    (out.parent/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'PASS V4: {out} | {duration:.2f}s | 1080x1920 | audio | {len(segments)} shots | review only')

if __name__=='__main__':main()
