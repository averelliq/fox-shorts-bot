"""V3 entrypoint: fix V2 dynamic frame hook and tighten avoidable TTS gaps."""
from pathlib import Path
source=Path(__file__).with_name('render_v3.py')
code=source.read_text(encoding='utf-8')
old='original_prop=v2.prop\n'
assert code.count(old)==1
code=code.replace(old,old+'original_make_frame=v2.make_frame\n',1)
old='image=v2.make_frame(t,seg,voice_length)'
assert code.count(old)==1
code=code.replace(old,'image=original_make_frame(t,seg,voice_length)',1)
# Compress only long gaps within each TTS segment, before V2 calculates
# audio-dependent frame counts. Leave a short pause; never stretch video audio.
needle='v2.make_frame=frame\n'
assert code.count(needle)==1
patch='''v2.make_frame=frame
_old_synth=v2.synth
async def _tight_synth(text,path):
    await _old_synth(text,path)
    cleaned=path.with_name(path.stem+'_tight.mp3')
    filt=('silenceremove=start_periods=1:start_duration=0:'
          'start_threshold=-38dB:start_silence=0.05:'
          'stop_periods=-1:stop_duration=0.48:'
          'stop_threshold=-38dB:stop_silence=0.12')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(path),
                    '-af',filt,'-c:a','libmp3lame','-q:a','3',str(cleaned)],check=True)
    if cleaned.stat().st_size<2000:raise RuntimeError('Voice cleanup produced empty audio')
    cleaned.replace(path)
v2.synth=_tight_synth
'''
code=code.replace(needle,patch,1)
exec(compile(code,str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
