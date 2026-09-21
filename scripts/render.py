"""Original 2D fox animation; Python/Pillow + FFmpeg + local eSpeak NG.
No API keys or third-party images. Requires pillow, ffmpeg, ffprobe, espeak-ng.
"""
import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=540,960,15
ROOT=Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def run(args): subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def duration(path):
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())
def wrap(draw,text,font,maxwidth):
    lines=[]; line=''
    for word in text.split():
        nextline=(line+' '+word).strip()
        if draw.textbbox((0,0),nextline,font=font)[2]>maxwidth and line:
            lines.append(line);line=word
        else:line=nextline
    if line:lines.append(line)
    return lines

def frame(t,seg,dur):
    scene=seg.get('scene','office'); emotion=seg.get('emotion','smug')
    im=Image.new('RGB',(W,H),'#17243A'); d=ImageDraw.Draw(im)
    top='#20304C' if scene=='office' else '#342643'
    for y in range(H):
        f=y/H; base=(int(int(top[1:3],16)*(1-f)+12*f),int(int(top[3:5],16)*(1-f)+19*f),int(int(top[5:7],16)*(1-f)+39*f))
        d.line((0,y,W,y),fill=base)
    d.rounded_rectangle((25,50,515,110),radius=19,fill='#283D55')
    d.text((W//2,80),'FOX vs ADULTING',font=ImageFont.truetype(FONT,23),anchor='mm',fill='#F9D976')
    if scene=='office':
        d.rounded_rectangle((40,190,500,590),radius=25,fill='#324C64',outline='#5D8195',width=4)
        d.rectangle((75,218,460,555),fill='#A7D5D7')
        d.ellipse((320,240,405,325),fill='#FCE6A6')
        for x in (135,228,340):d.rectangle((x,365,x+42,555),fill='#6C99A1')
        d.rectangle((0,720,W,960),fill='#483A43');d.rounded_rectangle((18,694,522,780),radius=22,fill='#947057')
        d.rounded_rectangle((340,622,480,705),radius=9,fill='#202B3C',outline='#8BA1B3',width=5)
    else:
        d.rounded_rectangle((38,190,500,550),radius=24,fill='#4F3B54')
        d.rounded_rectangle((77,228,460,500),radius=15,fill='#B1A0C0')
        d.ellipse((90,252,450,610),fill='#F7CB87')
        d.rectangle((0,748,W,960),fill='#564255')
        d.rounded_rectangle((55,692,245,803),radius=22,fill='#734F6A')
    sway=math.sin(t*3.7)*27
    d.polygon([(275,704),(425+sway,566),(472+sway,615),(422+sway,734),(311,800)],fill='#E67632')
    d.polygon([(444+sway,578),(472+sway,615),(448+sway,674),(406+sway,651)],fill='#FFF0D6')
    bob=math.sin(t*4)*5; ox=math.sin(t*1.3)*6
    d.ellipse((170+ox,550+bob,371+ox,834+bob),fill='#E77E32',outline='#A94C26',width=4)
    d.ellipse((229+ox,615+bob,315+ox,792+bob),fill='#FFF0D6')
    arm=math.sin(t*4.5)*19
    d.line((195+ox,642+bob,131+ox,712+bob+arm),fill='#E77E32',width=34)
    d.ellipse((112+ox,693+bob+arm,150+ox,731+bob+arm),fill='#F9AE65')
    d.line((343+ox,646+bob,398+ox,697+bob-arm),fill='#E77E32',width=32)
    d.ellipse((378+ox,679+bob-arm,416+ox,717+bob-arm),fill='#F9AE65')
    d.polygon([(179+ox,454+bob),(186+ox,262+bob),(267+ox,390+bob)],fill='#E77E32')
    d.polygon([(185+ox,418+bob),(193+ox,307+bob),(239+ox,393+bob)],fill='#F9AC90')
    d.polygon([(284+ox,382+bob),(367+ox,260+bob),(379+ox,463+bob)],fill='#E77E32')
    d.polygon([(319+ox,390+bob),(356+ox,308+bob),(366+ox,423+bob)],fill='#F9AC90')
    d.ellipse((150+ox,363+bob,397+ox,625+bob),fill='#EC873C',outline='#9F4B29',width=4)
    d.polygon([(159+ox,505+bob),(270+ox,564+bob),(388+ox,500+bob),(345+ox,606+bob),(190+ox,607+bob)],fill='#FFF0D6')
    blink=(t%3.7)<0.13
    for ex in (221,325):
        if blink:d.line((ex-19+ox,471+bob,ex+17+ox,471+bob),fill='#252637',width=6)
        else:
            d.ellipse((ex-17+ox,453+bob,ex+17+ox,496+bob),fill='white')
            d.ellipse((ex-5+ox,465+bob,ex+7+ox,488+bob),fill='#202332')
    if emotion=='surprised':d.ellipse((257+ox,548+bob,289+ox,587+bob),fill='#402B34')
    else:
        d.ellipse((258+ox,543+bob,290+ox,561+bob),fill='#302A32')
        mouth_open=(math.sin(t*17)>-0.08 and t<dur-0.15)
        if mouth_open:d.ellipse((256+ox,573+bob,292+ox,601+bob),fill='#5D293D')
        else:d.arc((252+ox,565+bob,298+ox,590+bob),0,180,fill='#4D2838',width=4)
    text=seg['text']; font=ImageFont.truetype(FONT,29); lines=wrap(d,text,font,466)
    y0=835-len(lines)*38
    d.rounded_rectangle((20,y0-20,520,870),radius=17,fill='#0D1829')
    for i,line in enumerate(lines):
        d.text((W//2,y0+i*38),line,font=font,anchor='mt',fill='#FFFFFF',stroke_width=1,stroke_fill='#16273B')
    return im

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--story',default=str(ROOT/'stories/episode.json'));ap.add_argument('--out',default=str(ROOT/'output/short.mp4'));ap.add_argument('--max-seconds',type=float,default=58);args=ap.parse_args()
    data=json.loads(Path(args.story).read_text(encoding='utf-8'));segments=data['segments']
    assert segments and all(isinstance(s.get('text'),str) and s['text'].strip() for s in segments)
    for binary in ['ffmpeg','ffprobe']:
        if not shutil.which(binary):raise RuntimeError(f'Missing binary: {binary}')
    tts=shutil.which('espeak-ng') or shutil.which('espeak')
    if not tts:raise RuntimeError('Missing voice engine: espeak-ng or espeak')
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);clips=[]
        for idx,seg in enumerate(segments):
            wav=td/f'{idx}.wav';run([tts,'-v','en-us','-s','155','-w',str(wav),seg['text']])
            voice_len=duration(wav);total=voice_len+0.45
            raw=td/f'{idx}.rgb';frames=math.ceil(total*FPS)
            with raw.open('wb') as f:
                for n in range(frames):f.write(frame(n/FPS,seg,total).tobytes())
            clip=td/f'{idx}.mp4'
            run(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i',str(raw),'-i',str(wav),'-filter_complex','[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];[1:a]apad[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','22','-r','30','-c:a','aac','-b:a','160k','-t',str(total),'-movflags','+faststart',str(clip)])
            clips.append(clip)
        manifest=td/'concat.txt';manifest.write_text(''.join(f"file '{c}'\n" for c in clips))
        run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(manifest),'-c','copy','-movflags','+faststart',str(out)])
    length=duration(out)
    meta=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(out)],capture_output=True,text=True,check=True).stdout)
    video=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'])==(1080,1920)
    assert 0<length<=args.max_seconds, f'Video length {length:.1f}s exceeds {args.max_seconds}s'
    assert any(s['codec_type']=='audio' for s in meta['streams'])
    (out.parent/'metadata.json').write_text(json.dumps({'title':data['title'],'description':data['description'],'duration_seconds':round(length,2),'width':1080,'height':1920,'quality_check':'passed'},indent=2),encoding='utf-8')
    print(f'PASS: {out} 1080x1920 with audio, {length:.2f}s')
if __name__=='__main__':main()
