# Root Cause: Protocol Violation Retry Loop

## The Bug

A kanban worker exits `rc=0` without calling `kanban_complete` or `kanban_block`.
The dispatcher detects this as a `protocol_violation`, auto-blocks the task
(failure_limit=1 via circuit-breaker), and emits `protocol_violation` → `gave_up`
events. But:

- `_has_sticky_block()` only looks for `{blocked, unblocked}` events
- Neither `protocol_violation` nor `gave_up` matches → returns `False`
- `recompute_ready()` sees a `blocked` task with no sticky guard
- Task has no parents → `all([])` = `True` → promoted back to `ready`
- Next tick respawns the worker → same failure → infinite loop

## The Fix

Add `protocol_violation` to the event kinds `_has_sticky_block()` checks.
If the most recent matching event is `protocol_violation` (not `unblocked`),
the block is sticky — `recompute_ready` will NOT auto-promote it.

## Event Sequence After Fix

1. Worker exits cleanly without completing → `protocol_violation` + `gave_up`
2. Task status = `blocked`
3. `_has_sticky_block()` sees `protocol_violation` → returns `True`
4. `recompute_ready()` skips this task → stays `blocked` ✓
5. Operator unblocks → `unblocked` event
6. `_has_sticky_block()` sees `unblocked` → returns `False`
7. `recompute_ready()` can promote ✓

## Risk Assessment

- Low risk: Only changes behavior for protocol-violation auto-blocks
- Existing `blocked`/`unblocked` event flow unchanged
- Operator `unblock` still clears all sticky state as expected
- Circuit-breaker blocks (genuine crashes, OOM, timeouts) remain non-sticky
