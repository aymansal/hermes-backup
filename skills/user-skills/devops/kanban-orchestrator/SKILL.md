---
name: kanban-orchestrator
description: Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role. For ImmoPilot payment/TVA/échéancier cards, see references/immopilot-moroccan-promoteur-payment-workflows.md. For product-intent UI pitfalls, see references/product-intent-review-pitfall.md.
version: 3.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing]
    related_skills: [kanban-worker]
---

> Ayman-specific doctrine: before orchestrating his raids, load `references/ayman-kanban-review-doctrine.md` for routing, review-gate scope, same-worker iteration, POS/business review policy, and phase-change reporting expectations. For frontend/UI preview links, also use `references/ayman-preview-gate-and-tunnel.md` to verify route/CSS health and open temporary outside-Tailscale Cloudflare tunnels safely. For long-running or suspicious cards, use `references/stuck-worker-diagnostics.md` to distinguish an active worker from a merely alive/stalled process before reporting status or reclaiming.

# Kanban Orchestrator — Decomposition Playbook

> The **core worker lifecycle** (including the `kanban_create` fan-out pattern and the "decompose, don't execute" rule) is auto-injected into every kanban process via the `KANBAN_GUIDANCE` system-prompt block. This skill is the deeper playbook when you're an orchestrator profile whose whole job is routing.

## Profiles are user-configured — not a fixed roster

Hermes setups vary widely. Some users run a single profile that does everything; some run a small fleet (`docker-worker`, `cron-worker`); some run a curated specialist team they've named themselves. There is **no default specialist roster** — the orchestrator skill does not know what profiles exist on this machine.

Before fanning out, you must ground the decomposition in the profiles that actually exist. The dispatcher silently fails to spawn unknown assignee names — it doesn't autocorrect, doesn't suggest, doesn't fall back. So a card assigned to `researcher` on a setup that only has `docker-worker` just sits in `ready` forever.

**Step 0: discover available profiles before planning.**

Use one of these:

- `hermes profile list` — prints the table of profiles configured on this machine. Run it through your terminal tool if you have one; otherwise ask the user.
- `kanban_list(assignee="<some-name>")` — sanity-check a single name. Returns an empty list (rather than an error) for an unknown assignee, so this only confirms a name you're already considering.
- **Just ask the user.** "What profiles do you have set up?" is a fine first turn when the goal needs more than one specialist.

Cache the result in your working memory for the rest of the conversation. Re-asking every turn wastes a tool call.

## When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.
7. **Ayman's 90-second/system-change threshold is crossed.** For Ayman, live repo work, Hermes Agent fixes, config edits, cron/Raid Timer changes, auth/credential-adjacent repairs, service restarts, deploys, or any task likely to exceed ~90 seconds must start as a Kanban raid before doing inline implementation. A local todo list is not a substitute for the board because it loses worker/reviewer accountability and durable audit trail.

If *none* of those apply — it's a small one-shot reasoning task — use `delegate_task` instead or answer the user directly.

See `references/ayman-hermes-ops-kanban-correction.md` for a concrete Hermes Agent ops raid pattern that was added after Ayman corrected an inline execution mistake. See `references/kanban-cli-quoting-and-preview-cache.md` for two recurring operator pitfalls: safe Kanban card creation with Markdown/backticks, and Next.js dev preview cache recovery after build/codegen runs. For Ayman's terse `Update?` cadence and immediate same-worker fix-loop after GPT-5.5 `BLOCKED` reviews, load `references/ayman-kanban-update-and-blocked-fix-loop.md`. For ImmoPilot ERP/UI card sequencing, preview verification, Convex generated API cleanliness, and Ayman's "hand polish later" boundary, also load `references/ayman-immopilot-erp-ui-kanban-lessons.md`.

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Risk-based review gates, not blind review of everything.** Require GPT-5.5 review for code/config/deploy/cron/service/auth/business-critical work, memory/skills/routing docs, and other durable future-behavior changes. Simple research/scraping that only gathers public information can be reported directly with sources, confidence, and official-vs-anecdotal labels.
- **Reviewer scope is narrow.** GPT-5.5 reviews only what the worker produced: result, diff, tests, artifacts, acceptance criteria, risks, and rollback notes. It must not redo the whole task unless the handoff is missing or suspicious.
- **Failed work iterates back to the same worker.** If review returns BLOCKED, create a fix card with the exact failures and route it back to the same worker model/profile that produced the failed output. Escalate models only after repeated failed iterations or explicit user approval.
- **Ayman model defaults:** coding uses OpenCode Go `deepseek-v4-flash`; UI/product/frontend visual work always uses `kimi-k2.6`; research/long docs use `kimi-k2.6`; memory/judgment curation uses `glm-5.1`; writing polish uses `minimax-m2.7`; final high-stakes review uses `gpt-5.5`. See `shadow-mission-orchestration/references/ayman-kanban-review-routing-doctrine.md` for the full doctrine.
- **Use task-appropriate worker profiles, not `default`, for labor.** `default`/GPT-5.5 is the General/reviewer lane unless Ayman explicitly approves using it for implementation. Before implementation cards, verify or create an OpenCode Go worker profile from the routing codex (for example DeepSeek/Qwen coder profiles). For UI/product/frontend visual tasks, route to Kimi K2.6 by default unless the user explicitly chooses otherwise. Do not assign coding labor to `default` merely because no specialist profile exists.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane instead of bundling unrelated work into a single implementer card.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked so the dispatcher can fan them out. Link only true data dependencies.
- **Never create dependent work as independent ready cards.** If a card must wait for another card, pass `parents=[...]` in the original `kanban_create` call. Do not create it first and link it later, and do not rely on prose like "wait for T1" inside the body.
- **If no specialist fits the available profiles, ask the user which profile to create or which existing profile to use.** Do not invent profile names; the dispatcher will silently drop unknown assignees.
- **Decompose, route, and summarize — that's the whole job.**

## Decomposition playbook

### Step 1 — Understand the goal

Ask clarifying questions if the goal is ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Step 2 — Sketch the task graph

Before creating anything, draft the graph out loud (in your response to the user). Treat every concrete workstream as a candidate card:

1. Extract the lanes from the request.
2. Map each lane to one of the profiles you discovered in Step 0. If a lane doesn't fit any existing profile, ask the user which to use or create.
3. Decide whether each lane is independent or gated by another lane.
4. Create independent lanes as parallel cards with no parent links.
5. Create synthesis/review/integration cards with parent links to the lanes they depend on. A child created with unfinished parents starts in `todo`; the dispatcher promotes it to `ready` only after every parent is done.

Examples of prompts that should fan out (using placeholder profile names — substitute whatever exists on the user's setup):

- "Build an app" → one card to a design-oriented profile for product/UI direction, one or two cards to engineering profiles for implementation, plus a later integration/review card if the user has a reviewer profile.
- "Fix blockers and check model variants" → one implementation card for the blocker fixes plus one discovery/research card for config/source verification. A final reviewer card can depend on both.
- "Research docs and implement" → a docs-research card can run in parallel with a codebase-discovery card; implementation waits only if it truly needs those findings.
- "Analyze this screenshot and find the related code" → one card to a vision-capable profile for the visual analysis while another searches the codebase.

Words like "also," "finally," or "and" do not automatically imply a dependency. They often mean "make sure this is covered before reporting back." Only link tasks when one card cannot start until another card's output exists.

Show the graph to the user before creating cards. Let them correct it — including which actual profile name should own each lane.

### Step 3 — Create tasks and link

Use the profile names from Step 0. The example below uses placeholders `<profile-A>`, `<profile-B>`, `<profile-C>` — replace them with what the user actually has.

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",  # whichever profile handles research on this setup
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<profile-A>",  # same profile, run in parallel
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<profile-B>",  # whichever profile does synthesis/analysis
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="<profile-C>",  # whichever profile drafts user-facing prose
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`. No manual coordination needed; the dispatcher and dependency engine handle it.

If the task graph has dependencies, create the parent cards first, capture their returned ids, and include those ids in the child card's `parents` list during the child `kanban_create` call. Avoid creating all cards in parallel and linking them afterward; that creates a window where the dispatcher can claim a child before its inputs exist.

### Step 4 — Complete your own task

If you were spawned as a task yourself (e.g. a planner profile was assigned `T0: "investigate Postgres migration"`), mark it done with a summary of what you created:

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes in parallel, 1 synthesis on their outputs, 1 prose draft on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "<profile-A>", "parents": []},
            "T2": {"assignee": "<profile-A>", "parents": []},
            "T3": {"assignee": "<profile-B>", "parents": ["T1", "T2"]},
            "T4": {"assignee": "<profile-C>", "parents": ["T3"]},
        },
    },
)
```

### Step 5 — Report back to the user

Tell them what you created in plain prose, naming the actual profiles you used:

> I've queued 4 tasks:
> - **T1** (`<profile-A>`): cost comparison
> - **T2** (`<profile-A>`): performance comparison, in parallel with T1
> - **T3** (`<profile-B>`): synthesizes T1 + T2 into a recommendation
> - **T4** (`<profile-C>`): turns T3 into a CTO memo
>
> The dispatcher will pick up T1 and T2 now. T3 starts when both finish. You'll get a gateway ping when T4 completes. Use the dashboard or `hermes kanban tail <id>` to follow along.

Report phase changes promptly and do not make Ayman ask for status after a gate changes. For Ayman, this is mandatory commander behavior, not optional polish: announce when a worker card starts, when a worker completes or blocks, when the reviewer starts, and when review returns PASS/BLOCKED. Do not wait for Ayman to ask "what happened?" after a card finishes; a quiet phase transition is a workflow failure. For high-stakes raids, also announce activation/config writes, cron creation, restart/deploy approval gates, crash/reclaim/retry events, and decision gates as soon as they happen. If Ayman says he is waiting, actively poll the board until the worker/reviewer completes or blocks, then report immediately.

For UI/frontend cards, a reviewer PASS is not the whole preview gate. Before telling Ayman to inspect a local web app, verify the served route and critical CSS/assets from the operator context. If the page is raw/unstyled, inspect asset refs first; for Next dev, stale `.next` output can produce HTML pointing at missing CSS. Ask before restarting/clearing cache. If Ayman asks to view outside Tailscale, prefer a temporary Cloudflare tunnel and verify the public route plus CSS before sharing the URL. See `references/ayman-preview-gate-and-tunnel.md`.

When Ayman ends a raid with “let’s go sleep” / “let go sleep”, perform the sleep-mode teardown: stop nonessential dev/preview/tunnel/idle-worker processes, verify no active required cards or dirty repo are being abandoned, and leave Hermes dashboard + Telegram gateway alive. See `references/ayman-raid-sleep-mode.md`.

## Common patterns

**Fan-out + fan-in (research → synthesize):** N research-style cards with no parents, one synthesis card with all of them as parents.

**Parallel implementation + validation:** one implementer card makes the change while one explorer/researcher card verifies config, docs, or source mapping. A reviewer card can depend on both. Do not make the implementer own unrelated verification just because the user mentioned both in one sentence.

**Pipeline with gates:** `planner → implementer → reviewer`. Each stage's `parents=[previous_task]`. Reviewer blocks or completes; if reviewer blocks, the operator unblocks with feedback and respawns.

**Same-profile queue:** N tasks, all assigned to the same profile, no dependencies between them. Dispatcher serializes — that profile processes them in priority order, accumulating experience in its own memory.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. The comment thread carries the full context.

## Pitfalls

**Inventing profile names that don't exist.** The dispatcher silently fails to spawn unknown assignees — the card just sits in `ready` forever. Always assign to a profile from your Step 0 discovery; ask the user if you're unsure.

**Bundling independent lanes into one card.** If the user asks for two independent outcomes, create two cards. Example: "fix blockers and check model variants" is not one fixer task; create a fixer/engineer card for the fixes and an explorer/researcher card for the variant check, then optionally gate review on both.

**Over-linking because of wording.** "Finally check X" may still be parallel with implementation if X is static config, docs, or source discovery. Link it after implementation only when the check depends on the implementation result.

**Forgetting dependency links.** If the task graph says `research -> implement -> review`, do not create all tasks as independent ready cards. Use parent links so implement/review cannot run before their inputs exist.

**Reassignment vs. new task.** If a reviewer blocks with "needs changes," create a NEW task linked from the reviewer's task — don't re-run the same task with a stern look. The new task is assigned to the original implementer profile.

**Review-required worker handoffs.** Some implementation workers intentionally mark themselves `blocked` with a `review-required` summary after producing files, because they are not allowed to declare PASS. The General may mark that worker task `done` only to unlock its dependent reviewer, but the completion summary must explicitly say "review-required handoff, not PASS" and no commit/deploy/user success claim may happen until the reviewer returns PASS and the General verifies gates. When Ayman asks `Update?`, inspect the live task state first; if GPT-5.5 already returned `BLOCKED`, create the same-worker fix card and dependent re-review card immediately instead of only reporting the failure. See `references/ayman-kanban-update-and-blocked-fix-loop.md`.

**Reviewer protocol violations can hide real verdicts.** If a review appears stuck but its log contains a clear PASS/BLOCKED verdict, recover the verdict instead of waiting blindly. Inspect `hermes kanban show`, `hermes kanban runs`, and `hermes kanban log <task_id> --tail 8000`; if the worker exited cleanly without calling `kanban_complete`/`kanban_block`, reclaim it, record the verdict manually, and route BLOCKED findings back to the same worker. See `references/reviewer-protocol-violation-recovery.md`.

**Blocked review completion can accidentally promote unsafe downstream children.** When you mark a failed/blocked review as `done` only to unlock a fix iteration, inspect the full board immediately after dispatch. Any operational child that should still wait (cron/Raid Timer, deploy, restart, production activation, warmup, config enablement) may be promoted because its parent is now `done`. Reclaim and re-block those children immediately with an explicit reason. Better: when possible, create the fix card as the only child of the failed review and keep deploy/activation cards blocked until a later PASS review.

**Argument order for links.** `kanban_link(parent_id=..., child_id=...)` — parent first. Mixing them up demotes the wrong task to `todo`.

**Don't pre-create the whole graph if the shape depends on intermediate findings.** If T3's structure depends on what T1 and T2 find, let T3 exist as a "synthesize findings" task whose own first step is to read parent handoffs and plan the rest. Orchestrators can spawn orchestrators.

**Tenant inheritance.** If `HERMES_TENANT` is set in your env, pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create` call so child tasks stay in the same namespace.

**CLI JSON shape, global flags, and card-body quoting.** `hermes kanban create --json` emits the task id under `id` in current CLI output, not `task_id`; parse `id` or verify the exact output before wiring dependencies. The `--board <slug>` flag belongs immediately after `hermes kanban` (for example `hermes kanban --board immopilot list`), not after subcommands like `list --board immopilot`. `hermes kanban create` takes the title as a positional argument, not `--title`. Avoid shell-interpolating Markdown card bodies containing backticks via `$(cat file)`; the shell can strip inline-code names or inject command output into review cards. Prefer subprocess argv arrays or verify `hermes kanban show <task_id>` immediately and add a corrective General comment if the body was polluted. See `references/kanban-cli-quoting-and-preview-cache.md`.

**Forced skills and profile scope.** Worker profiles can have profile-scoped skill libraries. A `--skill <name>` that exists for the operator/default profile may be unknown inside a worker profile and crash the card before useful work starts. For critical doctrine, either verify the skill is resolvable by that worker profile first, or embed the required doctrine/paths directly in the card body and omit `--skill`.

**Profile-scoped skill resolution.** Worker profiles may not resolve the same user-created skills as the default profile. Before passing `--skill <name>` to a Kanban worker, verify that the target profile can load that skill. If uncertain, embed the essential doctrine directly in the task body and use absolute paths to reference files. Do not let an unknown skill crash the first worker attempt.

**Profile-scoped side effects.** Worker profiles may run with their own HERMES_HOME / profile directories. If a card creates durable system state (cron jobs, profiles, config, files, subscriptions, credentials, service units), do not trust the worker's self-report alone. Verify the result from the controlling/default profile or the real production path before telling the user it is active. Example: a worker-created cron job can land under /home/ubuntu/.hermes/profiles/<worker>/cron/jobs.json, while the gateway scheduler reads /home/ubuntu/.hermes/cron/jobs.json; such a job appears successful to the worker but never fires. For gateway-visible raid timers, prefer creating the final cron job from the parent/operator context with the native cronjob tool, then have a reviewer inspect the default-profile hermes cron list and jobs file. See references/profile-scoped-cron-and-side-effects.md for the full verification pattern.

**Kanban SQLite DB corruption.** If the gateway log spams "kanban notifier tick failed: database disk image is malformed" every ~5 seconds, the kanban SQLite database is corrupted. This does not block chat but fills logs and disables board notifications. Recovery: see references/kanban-db-corruption-recovery.md.

## Recovering stuck workers

Before using destructive recovery actions, distinguish **alive** from **working**. A worker whose PID still exists may be stuck if it has no heartbeat, only `claim_extended` events with `reason: pid_alive`, stale log mtime, low CPU time, and log lines frozen around tool preparation such as `preparing kanban_complete`. Do not reassure the user that it is merely "running" in that case; report that it is alive but not progressing, preserve the files, and ask before interrupting/reclaiming. Use `references/stuck-worker-diagnostics.md` for the read-only diagnostic sequence and safe recovery pattern.

When a worker profile keeps crashing, hallucinating, or getting blocked by its own mistakes (usually: wrong model, missing skill, broken credential), the kanban dashboard flags the task with a ⚠ badge and opens a **Recovery** section in the drawer. Three primary actions:

1. **Reclaim** (or `hermes kanban reclaim <task_id>`) — abort the running worker immediately and reset the task to `ready`. The existing claim TTL is ~15 min; this is the fast path out.
2. **Reassign** (or `hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch the task to a different profile (one that exists on this setup) and let the dispatcher pick it up with a fresh worker.
3. **Change profile model** — the dashboard prints a copy-paste hint for `hermes -p <profile> model` since profile config lives on disk; edit it in a terminal, then Reclaim to retry with the new model.

Hallucination warnings appear on tasks where a worker's `kanban_complete(created_cards=[...])` claim included card ids that don't exist or weren't created by the worker's profile (the gate blocks the completion), or where the free-form summary references `t_<hex>` ids that don't resolve (advisory prose scan, non-blocking). Both produce audit events that persist even after recovery actions — the trail stays for debugging.
