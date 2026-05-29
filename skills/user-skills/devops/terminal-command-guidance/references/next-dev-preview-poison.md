# Next.js Dev Preview Poison Pattern

Use this when a Next dev preview appears to be running but the browser shows plain HTML, missing styling, hanging routes, or stale runtime errors after `pnpm build`, Convex codegen, or repeated route probes.

## Symptoms

- The dev server is listening on the expected port.
- Main HTML route may return `200`, but CSS returns `404`.
- Browser looks like raw/unstyled HTML.
- Dynamic routes may return `500` or hang while simpler routes return `200`.
- The HTML references assets such as `/_next/static/css/app/layout.css?...`, but fetching that asset fails.

## Read-only verification

```sh
ss -ltnp | grep ':3000' || true

for route in /app/sales/new /app/sales/test-sale /app; do
  file="/tmp/preview-${route//\//_}.html"
  code=$(curl --max-time 15 -sS -o "$file" -w '%{http_code}' "http://127.0.0.1:3000$route" || echo ERR)
  bytes=$(wc -c < "$file" 2>/dev/null || echo 0)
  echo "$route HTTP $code bytes=$bytes"
done

css=$(grep -o '/_next/static/css/[^" ]*\.css[^" ]*' /tmp/preview-_app_sales_new.html | head -n1 || true)
if [ -n "$css" ]; then
  curl --max-time 15 -sS -o /tmp/preview.css -w "css HTTP %{http_code} bytes=%{size_download} $css\n" "http://127.0.0.1:3000$css"
else
  echo 'css not found'
fi
```

## Safe resummon

Only after confirming the exact dev-server process tree for the preview port:

```sh
ps -ef | grep -E 'next dev|next-server' | grep -v grep
```

Terminate only the verified `next dev` / `next-server` processes for the preview port, then clear `.next` and restart under process tracking:

```sh
# Example for an app rooted at /home/ubuntu/immopilot
cd /home/ubuntu/immopilot

pids=$(ps -ef | awk '/next dev --hostname 0.0.0.0 --port 3000|next-server \(v15\.5\.18\)/ && !/awk/ {print $2}' | sort -u)
port_pids=$(ss -ltnp 2>/dev/null | awk '/:3000 / {print $NF}' | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | sort -u)
all_pids=$(printf '%s\n%s\n' "$pids" "$port_pids" | awk 'NF' | sort -u)
if [ -n "$all_pids" ]; then
  kill $all_pids 2>/dev/null || true
  sleep 1
fi
if ss -ltnp | grep ':3000' >/dev/null; then
  force_pids=$(ss -ltnp 2>/dev/null | awk '/:3000 / {print $NF}' | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | sort -u)
  kill -9 $force_pids 2>/dev/null || true
fi
rm -rf apps/web/.next
```

Then restart:

```sh
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
```

## Verification after restart

Probe both HTML and CSS before reporting success:

```sh
for route in /app/sales/new /app/sales/test-sale /app /app/sales /app/payments/new /app/clients /app/projects; do
  file="/tmp/preview-ok-${route//\//_}.html"
  code=$(curl --max-time 30 -sS -o "$file" -w '%{http_code}' "http://127.0.0.1:3000$route" || echo ERR)
  echo "$route HTTP $code"
done

css=$(grep -o '/_next/static/css/[^" ]*\.css[^" ]*' /tmp/preview-ok-_app_sales_new.html | head -n1 || true)
if [ -n "$css" ]; then
  curl --max-time 30 -sS -o /tmp/preview-ok.css -w "css HTTP %{http_code} bytes=%{size_download}\n" "http://127.0.0.1:3000$css"
fi
```

## Reporting

Say plainly: the server was alive but asset serving was poisoned; resummoning the preview and clearing `.next` fixed it. Do not claim the server was healthy just because a late `Local:` watch notification arrived.