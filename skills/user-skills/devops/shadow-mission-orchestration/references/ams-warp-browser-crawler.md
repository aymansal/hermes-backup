# AMS seasonal jobs: WARP + browser-use/Scrapy lesson

## Context

During an Austrian AMS seasonal agriculture job-finding mission, the VPS could reach `www.ams.at` but direct AMS job hosts timed out from the original Oracle/VPS route.

Ayman's preferred stack for these web missions remains:

- Human-like browsing: `browser-use` from `/home/ubuntu/browser-tools-lab` with OpenCode Go `kimi-k2.6`.
- Crawling/scraping: Scrapy from `/home/ubuntu/browser-tools-lab`.
- Native Hermes browser/web tools: fallback only.

## Durable technique

When a public site works in a normal browser path but job/API hosts time out from the VPS, test a network route change before rewriting scrapers.

For this session, Cloudflare WARP on Ubuntu 24.04 opened the AMS job hosts:

```sh
# Install official Cloudflare WARP client on Ubuntu noble
sudo install -d -m 0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
printf 'deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ noble main\n' | sudo tee /etc/apt/sources.list.d/cloudflare-client.list >/dev/null
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y cloudflare-warp

# Connect
warp-cli --accept-tos registration new
warp-cli --accept-tos mode warp
warp-cli --accept-tos connect
warp-cli --accept-tos status
```

Verification probes:

```sh
curl -4 -fsS --max-time 10 https://ifconfig.me
curl -6 -fsS --max-time 10 https://ifconfig.me
curl -I -L --connect-timeout 12 --max-time 25 https://jobs.ams.at/public/emps/
curl -I -L --connect-timeout 12 --max-time 25 https://jobroom.ams.or.at/jobroom/index_as.jsp
```

Stop WARP when no longer needed:

```sh
warp-cli disconnect
```

## AMS-specific findings

After WARP, these AMS hosts returned HTTP 200:

- `https://jobs.ams.at/public/emps/`
- `https://jobs.ams.at/public/emps/jobs`
- `https://jobs.ams.at/public/emps/jobs?query=landwirtschaft`
- `https://jobroom.ams.or.at/jobroom/index_as.jsp`

However, `https://jobs.ams.at/robots.txt` says:

```txt
user-agent: LinkedInBot
Allow: /public/emps/
Disallow:

user-agent: *
Allow: /public/emps/$
Disallow: /public/emps/
```

Interpretation: generic bots are allowed only at the exact `/public/emps/` root and disallowed under `/public/emps/`. Do not run Scrapy crawls against AMS job search/API paths unless an authorized route or explicit permission exists.

The Angular app bundle exposed the base API path `/public/emps/api`, but direct search calls such as:

```txt
/public/emps/api/search?query=landwirtschaft&page=0&pageSize=10
/public/emps/api/search?query=Saisonarbeit&page=0&pageSize=10
/public/emps/api/search?query=Erntehelfer&page=0&pageSize=10
```

returned HTTP 401 Unauthorized.

An open suggestions endpoint worked:

```txt
/public/emps/api/open/suggestions/jobtitle?query=landwirtschaft&count=10
```

and returned suggestions including:

- `FacharbeiterIn in der Landwirtschaft`
- `Landwirtschaftliche Hilfskraft (m/w)`

## Operational rule

For AMS job searches:

1. Use WARP or another trusted route only if the VPS cannot reach the job hosts.
2. Check `robots.txt` after access improves; do not assume network reachability means scraping is allowed.
3. Use `browser-use` for human-like/manual AMS browsing when scraping is disallowed.
4. Use Scrapy only for permitted sources or explicit authorized APIs.
5. Save reports under `/home/ubuntu/browser-tools-lab/outputs/<mission>/` with the route/access findings and robots/API evidence.

## Pitfalls

- Do not encode “AMS is unreachable” as a durable fact; WARP changed the reachability.
- Do not encode “Scrapy is broken” when the real blocker is robots/API authorization.
- Do not scrape disallowed AMS paths just because WARP makes them technically reachable.
- Avoid long combined network probes; if one endpoint hangs, use short isolated probes with connect/read timeouts.
