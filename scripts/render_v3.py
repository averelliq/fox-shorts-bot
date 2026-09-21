"""V3: enhance the tested V2 renderer; preview only, never publish."""
import json, math, subprocess, tempfile, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import render_v2 as v2

ROOT=Path(__file__).resolve().parents[1]
ORANGE='#F18B39'; INK='#263044'; CREAM='#FFF0D5'
original_background=v2.background
original_fox=v2.fox
original_boss=v2.boss
original_prop=v2.prop

def background(d,scene,t):
    original_background(d,scene,t)
    # Remove the permanent channel title, leaving useful screen space for acting.
    d.rectangle((0,0,540,151),fill={'office':'#1A304A','wifi':'#1B3C4B','boss':'#382942','rent':'#342A4E'}[scene])
    # Foreground perspective and continuity details in all four settings.
    for x in (27,513): d.line((x,770,x+(x-270)//3,957),fill='#786B71',width=2)
    if scene=='office':
        d.rounded_rectangle((20,152,195,247),radius=12,fill='#FFF0D5',outline='#24384A',width=3)
        d.text((107,178),'PAYCHECK',font=ImageFont.truetype(v2.FONT,17),fill=INK,anchor='mm')
        d.text((107,218),'$0.00',font=ImageFont.truetype(v2.FONT,24),fill='#B84A39',anchor='mm')
    if scene=='rent':d.rounded_rectangle((28,175,135,448),radius=8,fill='#4C405B',outline='#AD99B1',width=4)

def fox(d,t,action='talk',emotion='smug',x=210,y=573,scale=1.0,speaking=True):
    # V2 already contains jointed, consistent anatomical shapes. Extend that
    # identity with an invariant vest, badge, cheek freckles and hand action.
    original_fox(d,t,action,emotion,x,y,scale,speaking)
    bob=math.sin(t*(9 if action=='walk' else 4))*(10 if action=='walk' else 4)
    ox=math.sin(t*4)*5 if action!='walk' else math.sin(t*9)*13
    ox=x+ox; yy=y+bob
    def p(px,py):return (int(ox+(px-250)*scale),int(yy+(py-570)*scale))
    d.ellipse((*p(212,647),*p(291,779)),fill='#336F77',outline='#24525D',width=3)
    d.polygon([p(229,649),p(250,667),p(273,649),p(258,711),p(242,711)],fill=CREAM)
    d.ellipse((*p(244,700),*p(259,714)),fill='#F3D27C')
    for cheek in (186,321):
        for dy in (0,11):
            cx,cy=p(cheek,546+dy)
            d.ellipse((cx-2,cy-2,cx+2,cy+2),fill='#A85F40')
    if action=='show_phone':
        # Phone visibly follows the right hand, and its screen explains the gag.
        gesture=38*math.sin(t*6)
        cx,cy=p(367,645+gesture)
        d.rounded_rectangle((cx-30,cy-45,cx+30,cy+45),radius=6,fill='#243448',outline='#E2C58E',width=3)
        d.rounded_rectangle((cx-24,cy-35,cx+24,cy+30),radius=3,fill='#A8E5DB')
        d.text((cx,cy-15),'Wi-Fi',font=ImageFont.truetype(v2.FONT,10),fill=INK,anchor='mm')
        d.text((cx,cy+6),'SHARE',font=ImageFont.truetype(v2.FONT,10),fill=INK,anchor='mm')

def boss(d,t,emotion='stern'):
    original_boss(d,t,emotion)
    x=405;y=565+math.sin(t*3)*3
    if math.sin(t*12)>-.1:
        d.ellipse((x-15,y+20,x+19,y+53),fill='#763849')
    # Pointing arm gives a readable reaction to the Wi-Fi reveal.
    d.line((x-41,y+99,x-100,y+43+math.sin(t*6)*10),fill='#465776',width=19)

def prop(d,scene,t):
    original_prop(d,scene,t)
    if scene=='rent':
        if t>0.55:
            d.rounded_rectangle((286,247,507,329),radius=11,fill='#EFF4DF')
            d.text((396,288),'EXPOSURE?',font=ImageFont.truetype(v2.FONT,19),fill='#40594F',anchor='mm')
        # Landlord changes the locks in the final beat.
        if t>2.0:
            d.rounded_rectangle((54,305,144,445),radius=9,fill='#42394B',outline='#EBC682',width=3)
            d.ellipse((117,377,133,393),fill='#F6D680')

v2.background=background
v2.fox=fox
v2.boss=boss
v2.prop=prop

def frame(t,seg,voice_length):
    scene=seg['scene'];image=v2.make_frame(t,seg,voice_length)
    # V2 draws a full-sentence caption; cover it and draw timed 2-3 word groups.
    d=ImageDraw.Draw(image)
    d.rounded_rectangle((12,792,528,932),radius=17,fill='#111C2D')
    words=seg['text'].split();idx=min(len(words)-1,max(0,int(t/max(voice_length,.1)*len(words))))
    start=(idx//3)*3;active=words[start:start+3]
    font=ImageFont.truetype(v2.FONT,28)
    widths=[d.textbbox((0,0),word,font=font)[2] for word in active]
    xx=(540-sum(widths)-12*(len(active)-1))/2
    for j,(word,width) in enumerate(zip(active,widths)):
        d.text((int(xx),852),word,font=font,fill='#FFDB85' if start+j==idx else 'white',anchor='lm')
        xx+=width+12
    # Deliberate push-ins and varied framing across scenes.
    zoom={'office':1.03,'wifi':1.07,'boss':1.0,'rent':1.055}[scene]
    zoom+=min(.025,t/max(1,voice_length)*.025)
    if zoom>1:
        nw,nh=round(540*zoom),round(960*zoom)
        image=image.resize((nw,nh),Image.Resampling.BICUBIC)
        left=(nw-540)//2;top=(nh-960)//2
        image=image.crop((left,top,left+540,top+960))
    return image

v2.make_frame=frame

def effects(path,duration):
    sr=24000;n=int(duration*sr);signal=np.zeros(n,dtype=np.float64)
    for at,hz in ((.20,530),(3.2,950),(7.3,190),(10.6,300)):
        start=int(at*sr)
        if start>=n:continue
        t=np.arange(min(int(.29*sr),n-start))/sr
        chirp=np.sin(2*np.pi*(hz*t+190*t*t))*.075*np.exp(-t*16)
        signal[start:start+len(t)]+=chirp
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(signal,-1,1)*32767).astype('<i2').tobytes())

def run():
    # Keep the previously successful V2 voice, concatenation and resolution QC.
    v2.main()
    out=ROOT/'output/short.mp4';meta=ROOT/'output/metadata.json'
    details=json.loads(meta.read_text());duration=details['duration_seconds']
    with tempfile.TemporaryDirectory() as td:
        tone=Path(td)/'original_sfx.wav';mixed=Path(td)/'mixed.mp4'
        effects(tone,duration)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(out),'-i',str(tone),'-filter_complex','[0:a]volume=1[a];[1:a]volume=.30[b];[a][b]amix=inputs=2:duration=first:dropout_transition=0[m]','-map','0:v','-map','[m]','-c:v','copy','-c:a','aac','-b:a','160k',str(mixed)],check=True)
        mixed.replace(out)
    info=v2.probe(out);video=next(s for s in info['streams'] if s['codec_type']=='video')
    assert(video['width'],video['height'])==(1080,1920)
    assert any(s['codec_type']=='audio' for s in info['streams'])
    details.update({'version':'V3','original_synthesized_sfx':True,'per_phrase_caption_animation':True,'constant_brand_banner':False,'voice_human_listening_verified':False,'youtube_published':False,'technical_checks':'passed','human_review_required':True})
    meta.write_text(json.dumps(details,indent=2),encoding='utf-8')
    print('V3 QC PASS: 1080x1920, soundtrack, scene movement, original SFX; human voice and art review still required')

if __name__=='__main__':run()
