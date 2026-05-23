# Codex dashboard account label allocation

## Session signal

Ayman reported a Shadow Realm bug: with Codex accounts labeled `Gpt1`, `Gpt2`, `Gpt3`, `Gpt4`, deleting `Gpt3` left `Gpt1`, `Gpt2`, `Gpt4`. Adding a fourth account produced another `Gpt4` because the dashboard used `len(pool.entries()) + 1` for the display label.

Read-only inspection confirmed duplicate labels in `credential_pool.openai-codex`:

```text
#1 label='Gpt1' source=manual:dashboard_device_code
#2 label='Gpt2' source=manual:dashboard_device_code
#3 label='Gpt4' source=manual:dashboard_device_code
#4 label='Gpt4' source=manual:dashboard_device_code
```

The code path was `hermes_cli/web_server.py` in the dashboard Codex device-code login worker:

```python
label=f"Gpt{len(pool.entries()) + 1}"
```

## Durable lesson

Never allocate dashboard account display labels from the current pool length. Deletions make length-based labels collide. Labels are UI metadata; the stable identity is the credential id plus account fingerprint.

## Preferred fix pattern

Add a helper near the dashboard Codex login code, for example:

```python
def _next_codex_dashboard_label(entries) -> str:
    used: set[int] = set()
    for entry in entries:
        label = str(getattr(entry, "label", "") or "").strip()
        match = re.fullmatch(r"Gpt(\d+)", label, flags=re.IGNORECASE)
        if match:
            used.add(int(match.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"Gpt{n}"
```

Then replace:

```python
label=f"Gpt{len(pool.entries()) + 1}"
```

with:

```python
label=_next_codex_dashboard_label(pool.entries())
```

This fills the lowest free display slot (`Gpt1`, `Gpt2`, `Gpt4` -> `Gpt3`). If product policy changes to never reuse old numbers, persist a separate monotonic counter in auth metadata instead; do not infer it from current list length.

## Regression tests to add

Test at least these cases:

- Existing `Gpt1`, `Gpt2`, `Gpt4` -> next label `Gpt3`.
- Existing `Gpt1`, `Gpt2`, `Gpt3`, `Gpt4` -> next label `Gpt5`.
- Existing duplicate labels do not create another duplicate.
- Non-matching labels (custom names) are ignored safely.

## Quota metadata note

Dashboard re-login or account refresh can clear local exhaustion fields (`last_status`, `last_error_code`, `last_error_reset_at`) without resetting server-side ChatGPT/Codex quota. Treat the provider `/usage` endpoint as authoritative for reset times; local cooldown metadata is only Hermes routing state.
