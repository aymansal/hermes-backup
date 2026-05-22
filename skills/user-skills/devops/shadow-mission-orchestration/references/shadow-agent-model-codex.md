# Shadow Agent Model Codex

Last updated: 2026-05-22 17:07 UTC

Purpose: give the main GPT-5.5 General a grounded routing reference for Kanban shadows. This file decides which OpenCode Go model/profile to spawn by task type, and defines the review/iteration doctrine Ayman wants everywhere: Telegram, terminal, and Shadow Realm dashboard.

## Prime Directive — 90-second Kanban-first rule

If a user task is expected to take more than 90 seconds, require many tool calls, involve code/system changes, require web research, or benefit from review, the main General must not disappear into inline work. The General creates Kanban cards, replies immediately with task IDs, and stays available for chat.

Short tasks stay inline. Long tasks become raids.

## Universal raid lifecycle

1. Main GPT-5.5 General understands the request and estimates duration/risk.
2. If >90 seconds, create a Kanban raid board/card graph instead of working inline.
3. General chooses worker model/profile from this codex based on task type and evidence, not habit.
4. Worker shadow performs scoped work and leaves evidence in Kanban comments/summary.
5. General spawns or assigns a GPT-5.5 review shadow for final-grade review when stakes are high, or uses a DS/GLM reviewer for cheap first pass.
6. Reviewer reports to the General, not directly as final truth.
7. If review fails, General creates an iteration/fix card for the original worker with exact failures.
8. Loop until PASS, BLOCKED, or user decision is required.
9. General verifies the final state directly when there are external side effects.
10. General reports concise result to Ayman.

## Sources fetched / inspected

- Live OpenCode Go model endpoint: https://opencode.ai/zen/go/v1/models
- Hermes source: hermes_cli/models.py curated provider list and OpenCode API mode logic
- models.dev API snapshot: https://models.dev/api.json
- Public docs landing pages fetched: Z.ai docs, Moonshot/Kimi docs, MiniMax docs, Alibaba/Qwen docs
- Local Hermes config: Kanban gateway dispatch is enabled and default gateway is active

## Live OpenCode Go roster

OpenCode Go currently reports these model IDs:

- `minimax-m2.7`
- `minimax-m2.5`
- `kimi-k2.6`
- `kimi-k2.5`
- `glm-5.1`
- `glm-5`
- `deepseek-v4-pro`
- `deepseek-v4-flash`
- `qwen3.6-plus`
- `qwen3.5-plus`
- `mimo-v2-pro`
- `mimo-v2-omni`
- `mimo-v2.5-pro`
- `mimo-v2.5`
- `hy3-preview`

Hermes API mode rule: MiniMax models use `anthropic_messages`; other OpenCode Go models use `chat_completions`.

## Fast routing table

| Task type | Primary shadow | Fallback | Review shadow | Notes |
|---|---|---|---|---|
| Routine scout / inspect / read-only diagnostics | deepseek-v4-flash | qwen3.6-plus | glm-5.1 or gpt-5.5 | Fast and cheap. Good default for first pass. |
| Code implementation / bug fix | deepseek-v4-pro | qwen3.6-plus | gpt-5.5 | Use worktree/workspace; reviewer must inspect diff/tests. |
| Large docs / web / session synthesis | kimi-k2.6 | kimi-k2.5 | glm-5.1 or gpt-5.5 | Kimi first for long context and extraction. |
| Memory curation / preference extraction | glm-5.1 | glm-5 | gpt-5.5 | Conservative judgment; avoid pollution. |
| Policy/safety/approval triage | glm-5.1 | qwen3.6-plus | gpt-5.5 | GLM for cheap judgment, GPT-5.5 for final high-stakes. |
| Writing / final report / title generation | minimax-m2.7 | minimax-m2.5 | gpt-5.5 | Remember MiniMax requires Anthropic Messages mode. |
| Browser-use human-like navigation | kimi-k2.6 | qwen3.6-plus | gpt-5.5 | Matches Ayman preference: browser-use not Playwright/Puppeteer primary. |
| Scrapy/crawling implementation | deepseek-v4-pro | qwen3.6-plus | gpt-5.5 | Deterministic crawler code; review rate limits/safety. |
| Architecture plan | glm-5.1 | qwen3.6-plus | gpt-5.5 | Use multiple scouts if uncertain. |
| Model diversity / second opinion | mimo-v2.5-pro | mimo-v2-pro | gpt-5.5 | Use when General wants a different family opinion. |

## Model cards

### `minimax-m2.7`

Family: MiniMax M2.7
Hermes API mode: `anthropic_messages`
Suggested profile pattern: `shadow-minimax-writer`

Best for:
- title generation
- creative drafting
- long-form polished writing
- human-readable reports
- some Anthropic-style tool/message routing

Avoid for:
- OpenAI-only tool stacks unless Hermes api_mode is set correctly
- low-level code verification

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `302ai`, id `MiniMax-M2.7`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `False`
- provider `302ai`, id `MiniMax-M2.7-highspeed`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `False`
- provider `aihubmix`, id `coding-minimax-m2.7`, context `204800`, output `128100`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `coding-minimax-m2.7-free`, context `204800`, output `128100`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `coding-minimax-m2.7-highspeed`, context `204800`, output `128100`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `minimax-m2.5`

Family: MiniMax M2.5
Hermes API mode: `anthropic_messages`
Suggested profile pattern: `shadow-minimax-fallback`

Best for:
- fallback writer/summarizer
- creative copy
- report shaping

Avoid for:
- when M2.7 is available

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `hpc-ai`, id `minimax/minimax-m2.5`, context `1000000`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-cn`, id `MiniMax-M2.5`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `clarifai`, id `minimaxai/chat-completion/models/MiniMax-M2_5-high-throughput`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `crof`, id `minimax-m2.5`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `False`
- provider `deepinfra`, id `MiniMaxAI/MiniMax-M2.5`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `kimi-k2.6`

Family: Moonshot Kimi K2.6
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-kimi-researcher / shadow-kimi-browser / shadow-kimi-synth`

Best for:
- large-context reading and synthesis
- web extraction summarization
- research scouts
- browser-use planning/extraction
- long documents and session review

Avoid for:
- final safety review when exact policy judgment matters more than context size
- very small trivial tasks where cheaper flash model is enough

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `302ai`, id `kimi-k2-0905-preview`, context `262144`, output `262144`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `False`
- provider `302ai`, id `kimi-k2-thinking`, context `262144`, output `262144`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `302ai`, id `kimi-k2-thinking-turbo`, context `262144`, output `262144`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `abacus`, id `kimi-k2.5`, context `262144`, output `32768`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `kimi-k2.5`, context `262144`, output `32768`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `kimi-k2.5`

Family: Moonshot Kimi K2.5
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-kimi-fallback`

Best for:
- fallback for Kimi K2.6
- large-context research
- document summarization

Avoid for:
- tasks where K2.6 is available and reliability matters

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `abacus`, id `kimi-k2.5`, context `262144`, output `32768`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `kimi-k2.5`, context `262144`, output `32768`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-cn`, id `kimi-k2.5`, context `262144`, output `32768`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-cn`, id `kimi/kimi-k2.5`, context `262144`, output `262144`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-coding-plan`, id `kimi-k2.5`, context `262144`, output `32768`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `glm-5.1`

Family: Z.ai GLM 5.1
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-glm-curator / shadow-glm-judge`

Best for:
- judgment-heavy curation
- memory candidate filtering
- policy/safety gatekeeping
- approval decisions
- structured planning with conservative output

Avoid for:
- huge raw ingestion if Kimi has better context
- mechanical code edits where DeepSeek/Qwen is faster

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `siliconflow`, id `zai-org/GLM-5.1`, context `205000`, output `205000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `siliconflow-cn`, id `Pro/zai-org/GLM-5.1`, context `205000`, output `205000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `cortecs`, id `glm-5.1`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `novita-ai`, id `zai-org/glm-5.1`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `opencode`, id `glm-5.1`, context `204800`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `glm-5`

Family: Z.ai GLM 5
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-glm-fallback`

Best for:
- fallback for GLM 5.1
- curation
- planning
- classification
- triage

Avoid for:
- when GLM 5.1 is available for final judgment

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `poe`, id `novita/glm-5`, context `205000`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `siliconflow`, id `zai-org/GLM-5`, context `205000`, output `205000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `siliconflow`, id `zai-org/GLM-5.1`, context `205000`, output `205000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `siliconflow-cn`, id `Pro/zai-org/GLM-5`, context `205000`, output `205000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `siliconflow-cn`, id `Pro/zai-org/GLM-5.1`, context `205000`, output `205000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `deepseek-v4-pro`

Family: DeepSeek V4 Pro
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-deepseek-coder-pro`

Best for:
- serious coding implementation
- debugging
- repo inspection
- algorithmic work
- multi-file code tasks

Avoid for:
- tiny repetitive chores where flash is enough
- final review that should use GPT-5.5 shadow

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `cortecs`, id `deepseek-v4-pro`, context `1048576`, output `384000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `digitalocean`, id `deepseek-v4-pro`, context `1048576`, output `393216`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `gmicloud`, id `deepseek-ai/DeepSeek-V4-Pro`, context `1048576`, output `384000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `huggingface`, id `deepseek-ai/DeepSeek-V4-Pro`, context `1048576`, output `393216`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `kilo`, id `deepseek/deepseek-v4-pro`, context `1048576`, output `384000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `deepseek-v4-flash`

Family: DeepSeek V4 Flash
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-ds-flash-worker / shadow-ds-flash-reviewer`

Best for:
- fast Kanban scout tasks
- routine inspection
- compression-like synthesis
- first-pass implementation
- cheap review pass
- status dashboards

Avoid for:
- high-risk final judgment
- complex architecture decisions without review
- large-context docs if context is insufficient

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `cortecs`, id `deepseek-v4-flash`, context `1048576`, output `384000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `kilo`, id `deepseek/deepseek-v4-flash`, context `1048576`, output `384000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `kilo`, id `deepseek/deepseek-v4-flash:free`, context `1048576`, output `384000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `novita-ai`, id `deepseek/deepseek-v4-flash`, context `1048576`, output `393216`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `nvidia`, id `deepseek-ai/deepseek-v4-flash`, context `1048576`, output `393216`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `qwen3.6-plus`

Family: Qwen 3.6 Plus
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-qwen-engineer`

Best for:
- balanced reasoning + coding
- technical research
- Chinese/English bilingual tasks
- structured extraction
- backend implementation

Avoid for:
- final safety review if GPT-5.5 reviewer is required
- large raw web pages when Kimi is stronger

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `alibaba`, id `qwen3.6-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-cn`, id `qwen3.6-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-coding-plan`, id `qwen3.6-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-coding-plan-cn`, id `qwen3.6-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `auriko`, id `qwen-3.6-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `qwen3.5-plus`

Family: Qwen 3.5 Plus
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-qwen-fallback`

Best for:
- fallback balanced engineer
- classification
- technical summaries

Avoid for:
- when Qwen 3.6 Plus is available

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `zenmux`, id `qwen/qwen3.5-flash`, context `1020000`, output `1020000`, modalities `{'input': ['text', 'image'], 'output': ['text']}`, reasoning `False`
- provider `alibaba`, id `qwen3.5-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-cn`, id `qwen3.5-flash`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-cn`, id `qwen3.5-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`
- provider `alibaba-coding-plan`, id `qwen3.5-plus`, context `1000000`, output `65536`, modalities `{'input': ['text', 'image', 'video'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `mimo-v2-pro`

Family: Xiaomi MiMo V2 Pro
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-mimo-legacy`

Best for:
- fallback reasoning/model diversity

Avoid for:
- preferred model routing unless v2.5 unavailable

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `kilo`, id `xiaomi/mimo-v2-pro`, context `1048576`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `llmgateway`, id `mimo-v2-pro`, context `1048576`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `opencode`, id `mimo-v2-pro-free`, context `1048576`, output `64000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `opencode-go`, id `mimo-v2-pro`, context `1048576`, output `128000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `openrouter`, id `xiaomi/mimo-v2-pro`, context `1048576`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `mimo-v2-omni`

Family: Xiaomi MiMo V2 Omni
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-mimo-omni`

Best for:
- multimodal experiments if Hermes path supports required modality
- alternate scout

Avoid for:
- text-only Kanban work until benchmarked against Kimi/Qwen/DeepSeek

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `zenmux`, id `xiaomi/mimo-v2-omni`, context `265000`, output `265000`, modalities `{'input': ['text', 'image', 'audio', 'video', 'pdf'], 'output': ['text']}`, reasoning `True`
- provider `kilo`, id `xiaomi/mimo-v2-omni`, context `262144`, output `65536`, modalities `{'input': ['text', 'image', 'audio', 'video', 'pdf'], 'output': ['text']}`, reasoning `True`
- provider `llmgateway`, id `mimo-v2-omni`, context `262144`, output `131072`, modalities `{'input': ['text', 'image', 'audio', 'video', 'pdf'], 'output': ['text']}`, reasoning `True`
- provider `opencode`, id `mimo-v2-omni-free`, context `262144`, output `64000`, modalities `{'input': ['text', 'image', 'audio', 'pdf'], 'output': ['text']}`, reasoning `True`
- provider `opencode-go`, id `mimo-v2-omni`, context `262144`, output `128000`, modalities `{'input': ['text', 'image', 'audio', 'pdf'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `mimo-v2.5-pro`

Family: Xiaomi MiMo V2.5 Pro
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-mimo-scout`

Best for:
- general reasoning experiments
- alternate opinion scout
- model diversity checks

Avoid for:
- primary production path until benchmarked locally

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `vercel`, id `xiaomi/mimo-v2.5`, context `1050000`, output `131100`, modalities `{'input': ['text', 'image', 'audio', 'video'], 'output': ['text']}`, reasoning `True`
- provider `vercel`, id `xiaomi/mimo-v2.5-pro`, context `1050000`, output `131000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `coding-xiaomi-mimo-v2.5`, context `1048576`, output `131072`, modalities `{'input': ['text', 'image', 'audio', 'video'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `coding-xiaomi-mimo-v2.5-pro`, context `1048576`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `xiaomi-mimo-v2.5`, context `1048576`, output `131072`, modalities `{'input': ['text', 'image', 'audio', 'video'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `mimo-v2.5`

Family: Xiaomi MiMo V2.5
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-mimo-lite`

Best for:
- cheap/general fallback if available
- diversity scout

Avoid for:
- critical path until benchmarked

Nearby models.dev metadata examples (not always exact OpenCode Go IDs):
- provider `vercel`, id `xiaomi/mimo-v2.5`, context `1050000`, output `131100`, modalities `{'input': ['text', 'image', 'audio', 'video'], 'output': ['text']}`, reasoning `True`
- provider `vercel`, id `xiaomi/mimo-v2.5-pro`, context `1050000`, output `131000`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `coding-xiaomi-mimo-v2.5`, context `1048576`, output `131072`, modalities `{'input': ['text', 'image', 'audio', 'video'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `coding-xiaomi-mimo-v2.5-pro`, context `1048576`, output `131072`, modalities `{'input': ['text'], 'output': ['text']}`, reasoning `True`
- provider `aihubmix`, id `xiaomi-mimo-v2.5`, context `1048576`, output `131072`, modalities `{'input': ['text', 'image', 'audio', 'video'], 'output': ['text']}`, reasoning `True`

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

### `hy3-preview`

Family: hy3-preview
Hermes API mode: `chat_completions`
Suggested profile pattern: `shadow-hy3-preview`

Best for:
- unknown; benchmark before production routing

Avoid for:
- unbenchmarked critical work

Routing notes:
- Prefer empirical local success history over generic reputation when we have it.
- If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

## Kanban task templates

### Scout card

Title: `scout: <topic>`
Assignee: fast model such as `deepseek-v4-flash` or long-context `kimi-k2.6`
Body must include: objective, read-only scope, forbidden writes, required evidence, output format, escalation condition.

### Implement card

Title: `implement: <change>`
Assignee: `deepseek-v4-pro` or `qwen3.6-plus`
Body must include: exact files/repo/path if known, tests required, rollback notes, no secret exposure, and review-required handoff.

### Review card

Title: `review: <artifact/change>`
Assignee: GPT-5.5 shadow for high-stakes, otherwise `glm-5.1` or `deepseek-v4-flash` for first pass
Body must require: evidence checked, failures, PASS/BLOCKED verdict, exact iteration prompt if failed.

## GPT-5.5 General review doctrine

The General does not trust worker self-reports for side effects. For cron jobs, systemd services, config edits, GitHub changes, deployments, memory writes, and backups, the General verifies the real runtime path/profile itself before telling Ayman it succeeded.

Review checklist:
- Did the worker answer the exact card?
- Did it obey forbidden moves?
- Are files/commands/logs/tests cited?
- Did it avoid secrets and stale artifacts?
- If it changed system state, does the default/runtime profile actually see the change?
- Does the result need an iteration card?

## Profile creation doctrine

Profiles may be created dynamically by the General when a raid needs stable worker identity. Use lowercase descriptive names. Examples:

- `shadow-ds-scout` → deepseek-v4-flash
- `shadow-ds-coder` → deepseek-v4-pro
- `shadow-kimi-research` → kimi-k2.6
- `shadow-glm-curator` → glm-5.1
- `shadow-minimax-writer` → minimax-m2.7
- `shadow-qwen-engineer` → qwen3.6-plus

Before assigning a Kanban card, verify the profile exists with `hermes profile list`. If missing, create or configure it, then verify model/provider. Do not invent profile names and assume dispatch will work.

## Future improvement: empirical scoreboard

This codex should grow a local success table from real runs: task type, model, duration, pass/fail, reviewer notes, retries. Once enough data exists, route by local win rate first and public reputation second.
