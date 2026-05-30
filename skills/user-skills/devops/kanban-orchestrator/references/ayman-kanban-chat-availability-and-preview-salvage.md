# Ayman Kanban Chat Availability + Preview Salvage Lesson

Session lesson from an ImmoPilot UI raid where the General launched worker/reviewer cards but then stayed inside long polling and preview diagnostics, blocking normal chat availability.

## Trigger
Use this when Ayman has a Kanban raid running and the next step is worker/reviewer progress, preview health, or a review-required handoff.

## Lesson
Kanban is not just durable execution; for Ayman it is also a chat-availability contract. After spawning or starting workers/reviewers, the General should report the phase change and return control to chat instead of disappearing into long polling loops. Poll only for a short explicit checkpoint, or when Ayman asks for status/update.

## Correct pattern
1. Create/promote/dispatch worker or reviewer card.
2. Do one immediate verification that the card is in the expected state (`ready`, `running`, `blocked`, etc.).
3. Report concise state and current battle line.
4. Stop and remain available unless:
   - Ayman explicitly asks for live monitoring/status;
   - a phase transition already happened and requires action;
   - a short command is needed to finish a safe gate.
5. If review returns `BLOCKED`, create the same-worker fix and dependent re-review, then return with the new card ids/statuses.

## Preview salvage pattern
If review blocks on Next dev preview cache poison (`.next` missing vendor chunks, CSS 404, webpack-runtime missing chunks):

1. Distinguish code correctness from live preview health.
2. Do not claim PASS or commit while preview gate is required and failing.
3. Ask Ayman before stopping/restarting preview or deleting `.next`.
4. After approval:
   - stop only the affected Next dev process;
   - remove `apps/web/.next`;
   - restart `pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000`;
   - verify key app routes and CSS return HTTP 200;
   - comment the verified preview evidence onto the fix/review card;
   - complete only as review-required and start GPT-5.5 review.

## Reporting wording
Use explicit gates:
- Worker handoff: not PASS.
- Reviewer PASS/BLOCKED: accepted/rejected by GPT-5.5.
- Preview healthy: route/CSS gate only.
- Committed/pushed: final repository state.

Never blur these together.