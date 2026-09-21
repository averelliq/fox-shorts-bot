"""V2 production entrypoint: remove voice dead air without cutting internal pauses."""
import asyncio
import importlib.util
from pathlib import Path
import subprocess

source = Path(__file__).with_name('render_v2.py')
spec = importlib.util.spec_from_file_location('fox_render_v2', source)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
_original_synth = engine.synth


async def trimmed_synth(text, path):
    await _original_synth(text, path)
    path = Path(path)
    cleaned = path.with_name(path.stem + '_clean.mp3')
    audio_filter = ('silenceremove=start_periods=1:start_duration=0:'
                    'start_threshold=-38dB:start_silence=0.035,'
                    'areverse,'
                    'silenceremove=start_periods=1:start_duration=0:'
                    'start_threshold=-38dB:start_silence=0.035,'
                    'areverse')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(path),'-af',audio_filter,
                    '-c:a','libmp3lame','-q:a','3',str(cleaned)],check=True)
    if cleaned.stat().st_size < 2000:
        raise RuntimeError('Voice trimming yielded an empty clip; do not publish')
    cleaned.replace(path)


engine.synth = trimmed_synth
if __name__ == '__main__':
    engine.main()
