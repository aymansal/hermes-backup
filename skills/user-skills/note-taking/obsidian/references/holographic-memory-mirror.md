# Holographic memory mirror in Obsidian

Use this when the user wants Obsidian added to a Hermes/Holographic memory stack without replacing Holographic as the agent memory provider.

## Pattern

- Holographic remains the operational memory engine: structured facts, entities, relationships, and agent-side recall.
- Obsidian is a human-editable mirror: plain Markdown that lets the user inspect, correct, prune, and approve memory candidates.
- Avoid creating an Obsidian graph/map unless the user explicitly wants visualization. A single `memory.md` note is often enough.

## Recommended `memory.md` shape

```markdown
# memory

## Active memory summary
Short human-readable summary of durable facts currently believed by Hermes/Holographic.

## Entities
- [[Ayman]] — owner/operator
- [[Hermes]] — agent system
- [[Holographic Memory]] — operational memory engine
- [[Obsidian]] — human-editable mirror

## Pending memory candidates
Facts extracted from recent sessions that need human approval before being promoted.

## Approved for import
User-approved facts that Hermes may add to Holographic or compact memory.

## Rejected / stale
Candidates intentionally not saved.

## Editing rules
- Edit or delete wrong facts directly here.
- Move good candidates to “Approved for import”.
- Keep secrets, tokens, cookies, and passwords out of this file.
```

## Safe automation stance

For daily memory curation jobs, prefer a staged flow:

1. Review recent sessions.
2. Extract durable candidates only: stable preferences, architecture, environment facts, recurring corrections, project decisions, entity relationships.
3. Reject temporary artifacts: PR numbers, commit SHAs, one-off progress updates, transient errors, raw logs, and secrets.
4. Write candidates to Obsidian first.
5. Import to Holographic only after approval or after the filter is trusted.

This prevents silent memory pollution while still giving the user visibility and control.