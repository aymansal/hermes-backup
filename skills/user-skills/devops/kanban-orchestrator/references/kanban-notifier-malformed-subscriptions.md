# Kanban notifier malformed subscription rows

## Trigger

Use this reference when the gateway stays alive but `~/.hermes/logs/gateway.log` is spammed every few seconds with:

```text
kanban notifier tick failed: 'int' object has no attribute 'lower'
```

This is usually not a dead Comms Gate. It is a Kanban notification tick crashing on one malformed `kanban_notify_subs` row.

## Root cause pattern

The notifier expects `kanban_notify_subs.platform` to be a text platform name such as `telegram`, then calls `.lower()` while building active-platform filters or delivery routing. Legacy/corrupt rows can contain integers or other non-string values instead.

Observed live shape:

```text
board=immopilot task_id=task_comments platform=75  chat_id=None
board=immopilot task_id=task_events   platform=846 chat_id=None
board=immopilot task_id=task_runs     platform=210 chat_id=None
```

Those rows make old code effectively run `75.lower()`, crashing the whole notifier tick before valid subscriptions can be processed.

## Safe diagnostic sequence

Read-only first:

```bash
python - <<'PY'
from hermes_cli import kanban_db as kb
bad = []
for bm in kb.list_boards(include_archived=False):
    slug = bm.get('slug') or kb.DEFAULT_BOARD
    conn = kb.connect(board=slug)
    try:
        for sub in kb.list_notify_subs(conn):
            platform = sub.get('platform')
            if not isinstance(platform, str):
                bad.append((slug, sub.get('task_id'), platform, type(platform).__name__, sub.get('chat_id'), sub.get('thread_id')))
    finally:
        conn.close()
print('non_string_platform_subs', len(bad))
for row in bad[:50]:
    print(row)
PY
```

Check the notifier loop location:

- `gateway/run.py::_kanban_notifier_watcher`
- suspicious calls: `(sub.get("platform") or "").lower()` or `(sub["platform"] or "").lower()`

## Surgical code fix

Normalize platform values through `str(...)` before lowercasing, and do the same for adapter keys:

```python
active_platforms = {
    str(getattr(platform, "value", platform)).lower()
    for platform in self.adapters.keys()
}

platform = str(sub.get("platform") or "").lower()
platform_str = str(sub["platform"] or "").lower()
```

This keeps malformed rows from crashing the tick. Unknown platforms like `"75"` are skipped by the existing `platform not in active_platforms` / `Platform(...)` guards, while valid `telegram` rows still deliver.

Do **not** start by deleting rows from production boards unless the user approves. The code should be robust even when dirty legacy rows exist.

## Regression test pattern

Add a test to `tests/gateway/test_kanban_notifier.py` that:

1. Creates a valid completed Telegram subscription.
2. Inserts a malformed row directly into `kanban_notify_subs` with `platform=75`.
3. Runs one notifier tick.
4. Asserts the valid Telegram notification still sends once.

Target command:

```bash
python -m pytest tests/gateway/test_kanban_notifier.py -q -o 'addopts='
```

## Runtime verification

A code patch alone does not affect the already-running gateway process. After tests pass, ask Ayman before restarting/resummoning the gateway.

After approved restart, verify:

```bash
python - <<'PY'
from pathlib import Path
p = Path('/home/ubuntu/.hermes/logs/gateway.log')
for line in p.read_text(errors='replace').splitlines()[-120:]:
    if 'kanban notifier tick failed' in line:
        print(line)
PY
```

Then verify the Telegram route still replies in the intended topic, e.g. chat `-1003650104887`, thread `1`, before declaring the Comms Gate clean.
