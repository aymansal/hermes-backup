# Context7 MCP with Hermes

Use this note when adding Context7 documentation tools to Hermes via the native MCP client.

## Official server options

Context7 supports both:

1. Remote HTTP MCP endpoint:

```yaml
mcp_servers:
  context7:
    url: "https://mcp.context7.com/mcp"
    headers:
      CONTEXT7_API_KEY: "<SET_ON_RESTORE>"
    timeout: 120
    connect_timeout: 60
```

2. Local stdio server through npm:

```yaml
mcp_servers:
  context7:
    command: "npx"
    args: ["-y", "@upstash/context7-mcp", "--api-key", "<SET_ON_RESTORE>"]
```

## Recommended Hermes path

Prefer the remote HTTP endpoint when an API key is provided. Reason: the key can live under `headers.CONTEXT7_API_KEY`, which is easier for config sanitizers and backups to detect as a secret-bearing field than a CLI arg embedded in `args`.

## Verification

After adding the server:

```bash
hermes mcp test context7
hermes mcp list
```

Expected successful test shape:

```text
Transport: HTTP → https://mcp.context7.com/mcp
✓ Connected
✓ Tools discovered: 2
  resolve-library-id
  query-docs
```

## Activation

New Hermes sessions load MCP servers at startup. For an already-running gateway/session, use `/reload-mcp` if available, otherwise restart the gateway/session.

## Safety notes

- Do not echo the Context7 API key in summaries or logs.
- If timestamped config backups were created during setup, sanitize them or ensure the regular backup pipeline redacts secret-bearing fields.
- Lock `~/.hermes/config.yaml` permissions to owner-only when storing MCP headers with API keys.
