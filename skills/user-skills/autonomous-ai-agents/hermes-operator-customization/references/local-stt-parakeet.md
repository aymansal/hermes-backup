# Local STT with NVIDIA Parakeet for Hermes

Session lesson: when Ayman asks about "NVIDIA voice model" or "Parakeet v2", do not assume he means GPU/CUDA. NVIDIA Parakeet is an ASR model family and can be discussed separately from GPU acceleration.

## Hermes integration point

Hermes STT supports a local command bridge via:

```bash
HERMES_LOCAL_STT_COMMAND
```

and config:

```bash
hermes config set stt.enabled true
hermes config set stt.provider local_command
```

The command template is expected to receive placeholders such as `{input_path}` and `{output_dir}`. Hermes converts non-native audio with ffmpeg when needed, runs the configured command, then reads a `.txt` transcript from the output directory.

Use this bridge for Parakeet/Spokenly/custom ASR instead of forcing the built-in faster-whisper path.

## Read-only suitability checks

Before proposing install commands, inspect the live host:

```bash
lscpu | egrep 'Architecture|Model name|CPU\(s\)|Core|Socket|Thread'
free -h
df -h / /home 2>/dev/null
command -v ffmpeg >/dev/null && ffmpeg -version | head -1 || echo 'ffmpeg missing'
python - <<'PY'
import importlib.util, platform, sys
for m in ['nemo','nemo.collections.asr','transformers','torch','onnxruntime','soundfile','librosa']:
    try:
        spec = importlib.util.find_spec(m)
        print(f'{m}:', 'installed' if spec else 'missing')
    except Exception as e:
        print(f'{m}: error {e.__class__.__name__}: {e}')
print('python', sys.version.split()[0])
print('platform', platform.platform())
PY
```

## Oracle free-tier ARM guidance

Ayman's Oracle free-tier VPS class can be ARM64/aarch64 with 4 OCPUs and 24 GB RAM. For Parakeet 0.6B-class models, this is generally enough for short Telegram voice-message transcription:

- RAM: 24 GB is enough for the model plus runtime overhead.
- Disk: model files are roughly 2.5 GB; allow several GB more for caches and dependencies.
- CPU: acceptable for short voice notes, slower than a GPU/local PC.
- Swap: if swap is 0, propose an 8 GB swapfile before heavy ML installs/runs, but ask approval because it changes system config.
- Main risk: ARM64 Python dependency compatibility, especially NeMo/PyTorch/audio packages, not raw VPS capacity.

Do not record transient missing packages as durable facts; treat them as setup state.

## Model path choice

- Parakeet v2 (`nvidia/parakeet-tdt-0.6b-v2`) is NeMo-oriented and may hit ARM dependency friction.
- Parakeet v3 has Hugging Face Transformers support and may be easier to wire if the user is flexible.
- If the user specifically asks for v2, respect that and trial it in an isolated venv first.

## Safe install pattern

Do not install ML dependencies into the live Hermes environment first. Use an isolated venv:

```bash
python -m venv ~/.hermes/parakeet-venv
source ~/.hermes/parakeet-venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
```

Then install/test Parakeet dependencies inside that venv only, with a tiny audio sample. After success, create a wrapper:

```text
~/.hermes/scripts/parakeet_stt.py
```

The wrapper should accept input audio and output directory, run Parakeet, and write one `.txt` transcript into the output directory.

Example Hermes env rune shape:

```bash
HERMES_LOCAL_STT_COMMAND="/home/ubuntu/.hermes/parakeet-venv/bin/python /home/ubuntu/.hermes/scripts/parakeet_stt.py {input_path} {output_dir}"
```

Then restart the gateway and verify with a Telegram voice message.

## Alternative bridge

If the user's PC already runs Spokenly/Parakeet reliably, consider a Tailscale bridge:

```text
Hermes VPS -> Tailscale -> PC Parakeet STT endpoint -> transcript
```

This avoids ARM dependency risk but requires the PC to stay online and a small local API/command bridge.
