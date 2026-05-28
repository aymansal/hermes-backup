# Hermes friend-clone tool access verification

Use this reference when a restored/cloned Hermes instance says it cannot use `terminal`, `file`, `web`, or other tools even after `hermes tools enable ...`.

## Durable lesson

Hermes tool access is platform- and session-scoped:

- `hermes tools enable NAME` defaults to `--platform cli`.
- Telegram/gateway sessions need their own platform list: `--platform telegram`.
- Tool schemas are captured when the session/process starts; old sessions may still lack tools after config changes.
- A restored config may have correct top-level `toolsets` while `platform_toolsets.telegram` or `platform_toolsets.cli` is still restrictive.
- A one-shot check must use `-q` plus `-t`; `hermes chat -t ...` alone is not a proof of tool availability.

## Minimal fix commands

```bash
hermes tools enable terminal file web session_search delegation memory skills code_execution --platform cli
hermes tools enable terminal file web session_search delegation memory skills code_execution --platform telegram
hermes tools list --platform cli
hermes tools list --platform telegram
```

For Telegram/gateway testing:

```bash
hermes gateway restart
```

Then in Telegram:

```text
/new
check tailscale ip
```

For CLI one-shot testing:

```bash
hermes chat -q "Use your terminal tool to run: pwd && tailscale ip -4 || true" -t terminal,file,web,skills,memory,session_search,delegation,code_execution
```

## Audit when fixes still fail

Run a read-only audit before proposing another fix:

```bash
python3 - <<'PY'
from pathlib import Path
import os, shutil, subprocess, sys

print("=== Hermes Gate Audit ===")
print("which hermes:", shutil.which("hermes"))
print("HOME:", Path.home())
print("HERMES_HOME:", os.environ.get("HERMES_HOME") or "<unset>")

for cmd in [
    ["hermes", "config", "path"],
    ["hermes", "tools", "list", "--platform", "cli"],
    ["hermes", "tools", "list", "--platform", "telegram"],
]:
    print("\n$", " ".join(cmd))
    try:
        print(subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError as e:
        print(e.output)

cfg_path = subprocess.check_output(["hermes", "config", "path"], text=True).strip()
text = Path(cfg_path).read_text(errors="replace")
print("\nCONFIG:", cfg_path)
print("\n--- Lines mentioning toolsets ---")
for i, line in enumerate(text.splitlines(), 1):
    if "toolsets" in line or "platform_toolsets" in line or line.strip() in {"cli:", "telegram:"}:
        print(f"{i}: {line}")

print("=== END AUDIT ===")
PY
```

## Operator behavior

If Ayman already tried the generic fix, do not repeat it as if it is new. Say plainly that the prior path was incomplete, then switch to per-platform verification and proof commands.
