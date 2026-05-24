# ImmoPilot Monorepo Bootstrap Reference

Session-derived reference for creating the initial ImmoPilot repo skeleton without falling back into AI-generated spaghetti.

## Target repo shape

Default path used in the session:

```text
/home/ubuntu/immopilot
```

Initial package layout:

```text
apps/web
packages/ui
packages/config
convex
docs/doctrine
```

Use a Turborepo + pnpm workspace root with:

```text
package.json
pnpm-workspace.yaml
turbo.json
tsconfig.base.json
components.json
.env.example
```

## Doctrine import

Copy the living Ayman App Standard doctrine into the repo before feature implementation:

```bash
mkdir -p docs/doctrine
cp /home/ubuntu/.hermes/knowledge/ayman-app-standard/*.md docs/doctrine/
```

The important ImmoPilot doctrine set is:

```text
IMMOPILOT_SAAS_ARCHITECTURE.md
IMMOPILOT_CONVEX_SCHEMA_BLUEPRINT.md
IMMOPILOT_UI_DOCTRINE.md
IMMOPILOT_UI_REFERENCE_PACK.md
IMMOPILOT_DESIGN.md
IMMOPILOT_MVP_SCOPE.md
IMMOPILOT_PERMISSION_MODEL.md
IMMOPILOT_SCREEN_BLUEPRINTS.md
IMMOPILOT_KANBAN_EPICS.md
```

## First clean skeleton

Root scripts should include:

```json
{
  "dev": "turbo dev",
  "build": "turbo build",
  "lint": "turbo lint",
  "typecheck": "turbo typecheck",
  "format": "prettier --write .",
  "convex:dev": "convex dev",
  "convex:codegen": "convex codegen --typecheck disable",
  "check": "pnpm typecheck && pnpm lint && pnpm build"
}
```

Use `packageManager: pnpm@<exact version>` at the root. Do not let `pnpm init` leave `devEngines.packageManager.version: ^x.y.z`; pnpm can reject the caret version as an invalid package-manager specification.

## First UI shell

Create only a minimal product shell placeholder, not feature UI:

```text
ImmoPilot / ERP Core
Real-estate finance and project control for Moroccan developers.
```

Keep Sobhi out of product shell branding. Sobhi Immobilier is tenant/client data only.

## Shared UI package

Start `packages/ui` with a small `Button` component using ImmoPilot tokens. This validates workspace imports without pulling in a large component system too early.

Recommended variants:

```text
primary
secondary
danger
```

## Convex baseline

Create early baseline files:

```text
convex/schema.ts
convex/health.ts
convex/lib/errors.ts
convex/lib/permissions.ts
convex/lib/tenant.ts
convex/lib/audit.ts
```

Initial tables can be:

```text
organizations
memberships
auditLogs
```

Do not treat `convex/_generated` as available until `CONVEX_DEPLOYMENT` is configured. `convex codegen` can fail before `pnpm convex:dev` connects a deployment. That is not a blocker for the basic Next/UI skeleton if Convex helper files are not imported by the web app yet.

## Verification sequence

After scaffolding:

```bash
pnpm install
pnpm lint
pnpm typecheck
pnpm build
```

If pnpm blocks build scripts for dependencies such as `esbuild`, `sharp`, or `unrs-resolver`, the durable fix is to approve builds intentionally:

```bash
pnpm approve-builds --all
pnpm install
```

If ESLint scans generated Next output after a build, add generated-output ignores to the app ESLint flat config:

```js
{
  ignores: [".next/**", "next-env.d.ts", "node_modules/**"]
}
```

Also ignore TypeScript build info in `.gitignore`:

```text
*.tsbuildinfo
```

## Dev server smoke test

Run the web dev server and verify HTML is served:

```bash
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
curl -fsS --max-time 15 http://127.0.0.1:3000 | head -5
```

For Ayman's Tailscale VPS, expose the dev server on all interfaces and verify both local and Tailscale routes:

```bash
TAILSCALE_IP=$(tailscale ip -4)
curl -I --max-time 10 http://127.0.0.1:3000
curl -I --max-time 10 "http://${TAILSCALE_IP}:3000"
```

If the user cannot reach the site, do not guess firewall first. Check whether anything is listening on port 3000 and whether the dev process is alive:

```bash
ss -ltnp | grep ':3000' || true
ps -ef | grep -E 'next dev|next-server|immopilot' | grep -v grep || true
```

A common session outcome is simply that the dev server was stopped or never running; resummon it with the `--hostname 0.0.0.0` command above.

Stop the dev server after the smoke test unless the user asked to leave it running. If the user asks to sleep/shut down active work, stop the scoped ImmoPilot dev PIDs and verify no ports/processes remain:

```bash
ss -ltnp | grep -E ':(3000|3001|3210|3211|6791)\\b' || true
ps -ef | grep -E 'immopilot|next dev|next-server|convex dev|node.*convex' | grep -v grep || true
```

Hermes background-process watch notifications can arrive late. If a delayed “Ready” notification appears after shutdown, verify with `ss` and `ps` before assuming a server restarted.

## Convex cloud setup flow

When the user approves real Convex setup, run:

```bash
cd /home/ubuntu/immopilot
pnpm convex:dev
```

Expected interactive flow:

```text
Login or create an account
Device name: <default is OK>
Visit https://auth.convex.dev/device?user_code=XXXX-XXXX
create a new project
Project name: immopilot
cloud deployment
Set up Convex AI files? yes, if Ayman approves repo writes
```

After setup, verify generated files and env keys without printing secrets:

```bash
find convex/_generated -maxdepth 2 -type f | sort
python3 - <<'PY'
from pathlib import Path
for p in [Path('.env.local'), Path('.env')]:
    if p.exists():
        print(p)
        for line in p.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                print(line.split('=',1)[0]+'=[REDACTED]')
PY
```

Convex AI helper files (`AGENTS.md`, `CLAUDE.md`, `.agents/skills`, `convex/_generated/ai/guidelines.md`) are useful support, but they are subordinate to Ayman Senior App Forge and ImmoPilot tenant-isolation doctrine. Read Convex guidelines before Convex code, but do not let them override `organizationId` isolation, permissions, or audit requirements.

After Convex setup, run:

```bash
pnpm lint
pnpm typecheck
pnpm build
```

Commit only generated guidance/code files and lockfile changes. Do not commit `.env.local`.

## Commit gate

After passing lint/typecheck/build and smoke test:

```bash
git branch -m main
git add .
git commit -m "chore: initialize ImmoPilot monorepo skeleton"
```

## Next card after bootstrap

Do not jump into feature UI. The next card is:

```text
Epic 1 / Card 1.1: tenant-safe organization and membership schema/functions
```

Open the Convex Gate with `pnpm convex:dev` only when the user is ready to configure the deployment.
