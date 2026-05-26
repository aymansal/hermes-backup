---
name: business-workspace-management
description: Manage durable business/client workspace folders, project document placement, and safe file move/copy/delete workflows.
tags:
  - workspace
  - files
  - client-projects
  - document-management
---

# Business Workspace Management

## Purpose
Use this skill when the user asks to create or organize folders for a business, client, company, project, app/system, or document workspace. The goal is to keep work artifacts in stable, named locations instead of leaving them in transient cache paths.

## Required Inputs
- Business/workspace root, if not already known.
- Company/client/project/system name.
- Source file path when moving or placing an existing document.
- Whether the user wants **copy** or **move** semantics when handling an existing file.

## Safe Defaults
1. Use filesystem-safe names: title case words with hyphens, no spaces, no special punctuation unless the user specifies otherwise.
2. Create parent folders with `mkdir -p` semantics.
3. Verify created paths exist.
4. For documents from cache/temp paths, prefer moving into the durable workspace if the user says “put it inside” and later confirms it should not remain in cache.
5. If you accidentally copied when the user intended move, ask before deleting the original unless the user explicitly confirms deletion.

## Read-only / Verification Checks
Before destructive cleanup:
- Confirm the destination file exists and is non-empty.
- Confirm the exact original path to be deleted.
- State plainly that deletion removes the original/cache copy.

## Workflow
1. Identify the durable root folder for the business class of work.
2. Create a client/company folder under that root.
3. Create a subfolder per new system, app, module, or experiment when the user starts one.
4. Place related source documents inside the correct client/company/system folder.
5. Verify the final path.
6. If removing an old copy, require explicit user confirmation unless they already gave it.

## Ayman-Specific Workspace Notes
- See `references/ayman-pos-workspace.md` for the current POS business workspace convention.
- See `references/ayman-project-backup-boundaries.md` before answering whether Hermes backups contain POS/Samurai/Spana/ImmoPilot project code.

## Backup Boundary Doctrine
When Ayman asks whether a Hermes backup also includes business apps/projects, distinguish clearly between:
1. **Hermes recovery backup** — Hermes source/config/persona/skills/memory/kanban/cron/systemd/env template.
2. **Project/code backups** — actual app repositories/folders such as POS, Samurai, Spana, ImmoPilot, client systems.

Do not imply Hermes can resurrect project code just because it remembers project facts. Hermes memory and Skill Runes may contain notes, plans, and references, but not necessarily the actual repo files. Verify with the backup manifest or repo contents before answering.

## Common Pitfalls
- Do not leave important uploaded business documents only in `/home/ubuntu/.hermes/cache/documents/`; cache paths are transient work areas, not project homes.
- Do not silently delete originals after copying. Deletion is a destructive action and needs explicit confirmation.
- Do not create one flat folder containing every client artifact. Use client/company folders, then project/system subfolders.
- Do not store secrets in workspace notes, README files, skills, or memory.

## Expected Output
Report the exact path created or changed and whether verification passed. Keep it concise unless the user asks for a full structure report.
