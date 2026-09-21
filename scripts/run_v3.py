"""V3 entrypoint. Apply a one-line compatibility correction before execution.

V2 looks up its frame function dynamically. V3 must retain the original
V2 frame function before replacing it; otherwise it calls itself recursively.
"""
from pathlib import Path
source=Path(__file__).with_name('render_v3.py')
code=source.read_text(encoding='utf-8')
old='original_prop=v2.prop\n'
assert code.count(old)==1
code=code.replace(old,old+'original_make_frame=v2.make_frame\n',1)
old='image=v2.make_frame(t,seg,voice_length)'
assert code.count(old)==1
code=code.replace(old,'image=original_make_frame(t,seg,voice_length)',1)
exec(compile(code,str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
