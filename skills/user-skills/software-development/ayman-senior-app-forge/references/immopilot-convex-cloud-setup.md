# ImmoPilot Convex Cloud Setup Notes

Session-derived reference for opening the real Convex backend Gate for ImmoPilot.

## Context

Repo path used in this session:

```text
/home/ubuntu/immopilot
```

The repo already had a Turborepo/Next/Convex skeleton before this setup.

## Recommended setup flow

Run from the repo root:

```bash
pnpm convex:dev
```

Interactive choices used successfully:

1. `Login or create an account`
2. Accept the default device name, unless the operator wants a custom name.
3. Open the Convex device-auth URL shown by the CLI and authorize it in the browser.
4. `create a new project`
5. Project name: `immopilot`
6. `cloud deployment`
7. When asked `Set up Convex AI files? (guidelines, AGENTS.md, agent skills)`, answer `Y` for this repo.

Convex then generated/pushed functions and reported `Convex functions ready`.

## Expected files after successful setup

Generated or added:

```text
.env.local
AGENTS.md
CLAUDE.md
.agents/skills/
skills-lock.json
convex/_generated/api.d.ts
convex/_generated/api.js
convex/_generated/dataModel.d.ts
convex/_generated/server.d.ts
convex/_generated/server.js
convex/_generated/ai/guidelines.md
convex/_generated/ai/ai-files.state.json
```

Do not commit `.env.local`. It contains deployment-specific values such as:

```text
CONVEX_DEPLOYMENT=[REDACTED]
CONVEX_URL=[REDACTED]
CONVEX_SITE_URL=[REDACTED]
```

Commit the generated Convex AI guidance and generated API files when appropriate.

## Verification commands

```bash
pnpm lint
pnpm typecheck
pnpm build
```

Expected result: all PASS.

## AI guidance hierarchy

Convex may create `AGENTS.md`, `CLAUDE.md`, and Convex agent skills. Treat them as backend-specific support guidance.

They do not override:

1. Ayman Senior App Forge
2. ImmoPilot SaaS Architecture
3. Tenant Isolation and Reliability rules
4. ImmoPilot permission/screen/MVP doctrine

Convex guidelines are especially important for function syntax, validators, public vs internal functions, generated API references, and up-to-date Convex patterns.

## Tailscale preview note

For previewing the Next dev server over Tailscale, bind to all interfaces:

```bash
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
```

Verify both local and Tailscale paths:

```bash
curl -I --max-time 10 http://127.0.0.1:3000
curl -I --max-time 10 http://<TAILSCALE_IP>:3000
```

If the user sees `site can't be reached`, first check whether anything is listening on the port before assuming a Tailscale problem:

```bash
ss -ltnp | grep ':3000' || true
ps -ef | grep -E 'next dev|next-server' | grep -v grep || true
```

If port 3000 is open but `curl` hangs, release the stale Next dev process and resummon it. Avoid killing unrelated processes; verify PIDs first.
