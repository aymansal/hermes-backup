# Hermes curator model routing and reasoning effort

## Context
Ayman reported that the built-in Hermes Skill Curator produced weird saved/curated material when routed through GLM 5.1. Future Hermes auxiliary-routing work should treat curator quality as a high-judgment path, not a cheap metadata task.

## Verified findings
- Live config had `auxiliary.curator.provider: opencode-go` and `auxiliary.curator.model: glm-5.1`, with fallback `glm-5`.
- Hermes supports global `agent.reasoning_effort` values: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`.
- `xhigh` is the highest Hermes reasoning label.
- The native DeepSeek provider maps `xhigh`/`max` to top-level `reasoning_effort: max` and enables thinking for DeepSeek V4 models.
- OpenCode Go can serve many model slugs, but its generic provider profile does not carry Hermes' DeepSeek-specific `xhigh -> max` mapping. Do not assume `opencode-go + deepseek-v4-pro` guarantees max thinking payload unless verified by request tracing or provider docs.
- Hermes cron jobs that are `no_agent: true` do not use a model or reasoning effort. A deterministic script-only job cannot be made “DeepSeek V4 Pro xhigh” without redesigning it into an agent/LLM-backed job or adding an explicit LLM call in the script.

## Recommended policy
- Built-in Skill Curator: prefer DeepSeek V4 Pro with explicit `xhigh` reasoning through the native `deepseek` provider if available and authenticated.
- Daily Holographic Memory Curator cron: keep deterministic `no_agent` behavior unless Ayman explicitly asks to redesign it. If adding LLM review, start as proposal-only; do not let an LLM directly write memory facts until reviewed.

## Safe workflow before changing config
1. Load `hermes-agent` first for canonical Hermes commands.
2. Inspect current config and cron jobs read-only.
3. Verify the exact provider/model slug and whether the provider path actually sends reasoning effort.
4. Show the exact YAML/job diff before writing.
5. Back up `~/.hermes/config.yaml` before modifying.
6. Run `hermes config check` and a small curator smoke test if available.

## Pitfalls
- Do not trust the user's guessed model/provider slug without verification.
- Do not conflate the built-in Skill Curator with a daily memory-curator cron script.
- Do not make no-agent cron jobs model-specific; they intentionally skip the agent.
- Do not route high-judgment curation through a weak/cheap model just because it is background work.
