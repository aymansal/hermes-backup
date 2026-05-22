---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Hermes/Holographic memory mirror

When the user wants Obsidian added to a Hermes/Holographic memory setup, do not treat Obsidian as a replacement memory provider. Use Obsidian as a human-editable Markdown mirror for visibility, review, and correction while Holographic remains the agent-side memory engine.

Default to one readable `memory.md` note rather than a graph/map unless the user explicitly asks for visualization. The note should expose active memory summaries, entities, pending memory candidates, approved imports, rejected/stale candidates, and editing rules. For daily memory-curation automation, prefer a staged flow: extract durable candidates from recent sessions, write them to the note app for review, and only promote approved/high-confidence facts into Holographic. Never save secrets or transient artifacts.

### Cross-device note app reality check

Before writing any mirror file, verify where the user's real note app graph/vault lives and how the VPS reaches it. Creating `/home/ubuntu/.../memory.md` on the VPS does **not** make it appear in Obsidian/Logseq/Joplin on the user's PC unless that exact folder is synced or mounted. If the app is on the user's PC, discuss the sync bridge first:

- Obsidian/Logseq: file-based graphs; need Syncthing, Git, cloud drive, official sync, or an API/plugin bridge.
- Logseq: open-source and local-first; official sync may require account/paid plan, so Syncthing/Git are common free bridges.
- Joplin: often better when the user wants native free sync plus VPS automation, because it has desktop/mobile apps, built-in sync to free providers, and a CLI usable from the VPS.

If the user asks for “native, free sync” rather than local file sync, do not assume Obsidian/Logseq is ideal; propose Joplin as a likely better fit and explain the trade-off.

If the user abandons note-app mirroring and only wants daily session reading, stop pushing Obsidian/Logseq/Joplin. Switch to a Holographic-only curator pattern: scheduled job reads recent sessions, extracts durable high-confidence facts, deduplicates against fact_store, writes only to fact_store, and reports what was saved/rejected. This avoids sync complexity and memory pollution.

See `references/holographic-memory-mirror.md` for the recommended page shape and automation policy.
