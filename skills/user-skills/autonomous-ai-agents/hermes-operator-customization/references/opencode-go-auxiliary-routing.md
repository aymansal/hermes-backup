# OpenCode Go auxiliary routing for Hermes quota control

Session lesson: when Ayman wants to reduce OpenAI Codex quota burn in Hermes, treat this as Hermes auxiliary-model routing first, not a main-model switch.

## Read-only inspection sequence

Load the protected `hermes-agent` skill first for canonical commands, then inspect before editing:

```bash
hermes config path
hermes config env-path
hermes --version
hermes status --all
```

Read `/home/ubuntu/.hermes/config.yaml` and focus on:

```yaml
model:
auxiliary:
  compression:
  web_extract:
  approval:
  title_generation:
  curator:
compression:
curator:
approvals:
delegation:
```

Check only whether provider keys are active in `.env`; never print values. Relevant keys include:

```text
OPENCODE_GO_API_KEY
GLM_API_KEY
KIMI_API_KEY
DEEPSEEK_API_KEY
OPENROUTER_API_KEY
```

Do not count commented template lines as configured keys. Lines like `# OPENCODE_GO_API_KEY=` or commented base URLs are documentation only. Verify the live runtime can actually read the variable by sourcing `.env` and checking only presence/length/status, not value. If Hermes says `Provider 'opencode-go' is set in config.yaml but no API key was found`, the model routing may be correct but the Access Key is not active in the process environment.

## Confirm provider/model support locally

In Hermes v0.14.0, OpenCode Go provider id is `opencode-go` and the provider profile uses `OPENCODE_GO_API_KEY` with base URL `https://opencode.ai/zen/go/v1`.

The curated OpenCode Go model list observed in `hermes_cli/models.py` included:

```text
kimi-k2.6
kimi-k2.5
glm-5.1
glm-5
mimo-v2.5-pro
mimo-v2.5
mimo-v2-pro
mimo-v2-omni
minimax-m2.7
minimax-m2.5
qwen3.6-plus
qwen3.5-plus
```

`deepseek-v4-flash` was not in that curated list, but Hermes' OpenCode Go normalization did accept arbitrary model IDs and routed `deepseek-v4-flash` as `chat_completions`. Treat it as plausible but unconfirmed unless a live provider model-list or completion test proves it.

## Recommended tactical mapping

Mental model:

- Compression = huge input survival → `deepseek-v4-flash` if OpenCode Go serves it and returns usable final `content` under compression budgets.
- Memory / curator = judgment → `glm-5.1`, fallback `glm-5`.
- Web/doc extraction = long structured summarization → `kimi-k2.6`, fallback `kimi-k2.5`.
- Approval / safety = judgment, but the current Hermes smart-approval path uses a very small hardcoded output budget (`max_tokens=16` in `tools/approval.py` as observed in v0.14.0). Reasoning-heavy GLM models can spend that entire budget in `reasoning_content` and return empty final `content`, causing escalation. Either patch the approval budget upward (for example 128) if keeping GLM, or use a model that emits the final label within 16 tokens (live test: `qwen3.5-plus` returned `APPROVE`).
- Tiny metadata/title generation = cheap fast model that returns final content reliably. Live OpenCode Go tests showed `deepseek-v4-flash` can return `None` for real Hermes title generation because it spends the budget in reasoning; `minimax-m2.7` and `qwen3.5-plus` produced clean titles.

Draft config shape (pre-live-test baseline; adjust title/approval per the pitfalls below):

```yaml
auxiliary:
  compression:
    provider: opencode-go
    model: deepseek-v4-flash
    timeout: 180
    fallback_chain:
      - provider: opencode-go
        model: glm-5
      - provider: opencode-go
        model: kimi-k2.6

  curator:
    provider: opencode-go
    model: glm-5.1
    timeout: 600
    fallback_chain:
      - provider: opencode-go
        model: glm-5

  web_extract:
    provider: opencode-go
    model: kimi-k2.6
    timeout: 360
    fallback_chain:
      - provider: opencode-go
        model: kimi-k2.5
      - provider: opencode-go
        model: deepseek-v4-flash

  approval:
    provider: opencode-go
    model: glm-5.1
    timeout: 30
    fallback_chain:
      - provider: opencode-go
        model: glm-5

  title_generation:
    provider: opencode-go
    model: deepseek-v4-flash
    timeout: 30
    fallback_chain:
      - provider: opencode-go
        model: glm-5

compression:
  enabled: true
  threshold: 0.55
  target_ratio: 0.15
  protect_last_n: 8
  hygiene_hard_message_limit: 400
  protect_first_n: 3
  abort_on_summary_failure: false
```

## Safety / workflow rule for Ayman

Ayman wants proposed plans explained before applying Hermes configuration changes. For this class of task:

1. Phase 1: read-only scan and report exact current config/provider/model support.
2. Phase 2: show the exact YAML patch.
3. Phase 3: apply only after approval.
4. If Ayman has already provided the relevant provider Access Key for the approved setup, install it into `.env` during Phase 3 instead of later reporting the key as missing. He considers the Tailscale-protected Hermes chat acceptable for sharing Access Keys; still never echo, log, or save the key in memory/skills.
5. Always create a backup of `config.yaml` before writing and a backup of `.env` before writing Access Keys.
6. Run `hermes config check` after writing.
7. Restart gateway/dashboard only if required and after config check passes.

## Smoke-test auxiliary Gates after config changes

After writing `config.yaml`, installing the required Access Key in `.env`, and resummoning the gateway if needed, test each configured auxiliary task directly. Do not stop at HTTP 200; inspect `content`, `finish_reason`, reported model, and whether the response used `reasoning_content`.

A reusable helper is packaged with this skill:

```bash
cd /home/ubuntu/.hermes/hermes-agent
set -a
. /home/ubuntu/.hermes/.env >/dev/null 2>&1 || true
set +a
venv/bin/python /home/ubuntu/.hermes/skills/autonomous-ai-agents/hermes-operator-customization/scripts/test_auxiliary_routing.py
```

Expected success shape: JSON lines with `ok: true`, non-empty `content` for content-producing tasks, and sane `finish_reason`. If every task fails immediately with “no API key was found,” fix `.env` activation before debugging model slugs.

Live OpenCode Go observations from this session:

- `deepseek-v4-flash` is reachable through OpenCode Go and reported HTTP 200/model `deepseek-v4-flash`, but can spend short output budgets in `reasoning_content` before emitting final `content`.
- Real `agent.title_generator.generate_title()` returned `None` with `deepseek-v4-flash`; `minimax-m2.7`, `qwen3.5-plus`, and GLM produced usable titles in direct tests.
- `tools.approval._smart_approve()` returned `escalate` for both safe and risky examples when approval was routed to `glm-5.1`, because `_smart_approve` calls the auxiliary model with `max_tokens=16`; GLM used that budget for reasoning and emitted no final label.
- `web_extract` with `kimi-k2.6` and `curator` with `glm-5.1` worked when given normal task-sized output budgets.

When testing model substitutions for constrained tasks, use the same max-token budget as the real Hermes call. For approval specifically, test with `max_tokens=16` unless the code has been patched.

## Quota warning caveat

Codex quota tracking exists via `agent/codex_quota.py` and the dashboard endpoint `/api/model/quota`, but a simple built-in config key for “warn when 5h remaining <= 30% before tool-heavy work” was not found during this session. Treat that as a separate code patch or Raid Timer/watchdog, not part of auxiliary model routing.

## Pitfalls

- Do not expose pasted API keys in summaries, patches, logs, or skill references. Use env vars/placeholders only.
- Do not claim `deepseek-v4-flash` is confirmed on OpenCode Go solely because normalization accepts it; verify with a live completion/model-list test when safe.
- Do not edit protected bundled skills like `hermes-agent`; put user-specific Hermes operating patterns in this companion skill.
