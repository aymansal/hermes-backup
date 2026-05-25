# ImmoPilot dev preview and Convex auth notes

Session-derived reference for previewing the local ImmoPilot app over Tailscale and starting Convex auth safely.

## Dev preview over Tailscale

When Ayman asks to see the website from his device:

1. Check whether the dev server is already listening.
2. If not listening, start it bound to all interfaces, not localhost only.
3. Verify both local and Tailscale routes before reporting the URL.

Known-good command:

```bash
cd /home/ubuntu/immopilot
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
```

Verification pattern:

```bash
ss -ltnp | grep ':3000' || true
curl -I --max-time 10 http://127.0.0.1:3000
curl -I --max-time 10 http://100.72.70.121:3000
```

Expected success:

```text
LISTEN ... 0.0.0.0:3000
HTTP/1.1 200 OK
```

If Ayman says the site cannot be reached, do not assume Tailscale is broken. First verify the process is still running. In the observed session, the root cause was simply that the dev server had stopped; restarting it fixed the preview.

Report clearly:

- whether a process is listening
- whether local curl passes
- whether Tailscale curl passes from the VPS itself
- exact URL to open: `http://100.72.70.121:3000`

## Convex auth flow

When starting real Convex setup:

```bash
cd /home/ubuntu/immopilot
pnpm convex:dev
```

Run interactively with a PTY if using Hermes process tools. Convex may prompt:

```text
Welcome to Convex! Would you like to login to your account?
❯ Start without an account (run Convex locally)
  Login or create an account
```

If Ayman approved real account auth, choose:

```text
Login or create an account
```

Accept the default device name unless there is a reason to customize it.

Convex then prints a short-lived device login URL and code, e.g.:

```text
Visit https://auth.convex.dev/device?user_code=XXXX-XXXX
You should see the following code which expires in 299 seconds: XXXX-XXXX
```

Send Ayman the link and code, then wait for him to say done before continuing the running Convex process.

Do not expose or store tokens. Device codes are short-lived auth prompts, not durable secrets, but still keep summaries minimal.

## Kanban nuance for bootstrap work

For this app class, full Kanban can be consciously skipped for low-risk local bootstrap actions such as creating a new local repo skeleton, copying doctrine, starting a dev preview, resuming previously stopped dev processes, or read-only checks. The important requirement is that the commander states the judgment explicitly. Forgetting the Kanban rule is a process failure; intentionally skipping it with a reason is acceptable.

## Related reference

For the exact stop/resume pattern used when Ayman says to put ImmoPilot to sleep or wake what was stopped yesterday, see:

```text
references/immopilot-dev-shadows-sleep-wake.md
```
