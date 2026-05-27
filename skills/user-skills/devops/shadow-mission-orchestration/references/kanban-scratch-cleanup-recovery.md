# Kanban scratch cleanup recovery incident pattern

Use this reference when a Kanban task or review accidentally classifies a real project directory as a scratch workspace, or when a project folder disappears after task completion.

## Failure signature

- Final gates or commit suddenly fail with missing project root files, e.g. no `package.json`, no workspace file, or `fatal: not a git repository`.
- A still-running dev server may keep serving from a deleted inode such as `/project/apps/web (deleted)`.
- Kanban task DB shows `workspace_kind = scratch` with `workspace_path` pointing at a real project directory.
- Cleanup code removes scratch workspaces with `rmtree`, so a wrong `workspace_path` can delete the Core Crystal.

## Correct operator response

1. Stop and report immediately. Do not spend many minutes silently digging.
2. Do not kill the still-running dev server until the source recovery path is clear.
3. Identify the exact task that completed near the deletion timestamp and inspect its workspace fields.
4. Look for surviving source copies in agent/temp workspaces and worker artifacts.
5. Restore into the real project path only after confirming the copy has expected root files.
6. Recreate Git history honestly: explain whether original `.git` history survived or whether this is a new recovery baseline.
7. Reapply/reconstruct missing recent work from Kanban logs, worker reports, session evidence, and recovered files.
8. Run gates and route smoke tests before restarting the preview.
9. Patch the cleanup guardrail so scratch cleanup refuses to delete paths outside the Kanban workspaces root.

## Communication rule

Never describe recovery as the folder "reappeared" or imply mystery. Say plainly:

- "The folder was deleted by scratch cleanup."
- "I restored the base app from a surviving temp copy."
- "The original Git history did/did not survive."
- "The latest feature code was restored/reconstructed into a new recovery commit."

If the user asks how recovery happened, answer provenance first: which copy/source was used, what survived, what was recreated, and what remains uncertain.

When Ayman is trying to understand a serious incident, switch to plain English first. Avoid code blocks, commit jargon, and vague system phrasing unless he asks for evidence. Answer the exact questions directly: original folder vs temp copy, Git history vs source state, what the reviewer was reviewing, whether the latest worker changes survived, and what still needs redo. If a previous explanation used ambiguous language like "reappeared", correct it explicitly.
