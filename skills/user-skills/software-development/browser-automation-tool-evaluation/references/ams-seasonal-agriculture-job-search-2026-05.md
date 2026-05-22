# AMS seasonal agriculture job-search probe — 2026-05

## Context

Ayman asked to test finding seasonal agriculture jobs using the established browser stack:

- human-like browsing: `browser-use`
- scraping/crawling: `Scrapy`
- lab path: `/home/ubuntu/browser-tools-lab`
- browser-use model route: OpenCode Go, model `kimi-k2.6`
- native Hermes browser/web tools only as fallback

## Durable workflow lessons

1. For job sites, separate three phases:
   - **Access/robots probe**: check homepage, robots.txt, public job URLs, and TCP reachability before crawling.
   - **Human route probe**: use browser-use to verify the site navigation path a real user would take.
   - **Crawler extraction**: only write Scrapy spiders after a reachable, allowed, public endpoint or page shape is confirmed.
2. Do not crawl paths disallowed by robots.txt, do not bypass login/CAPTCHA/Cloudflare, and do not treat access restrictions as scraper bugs.
3. If the official job platform is unreachable from the VPS, report that as network reachability evidence and offer running the same probe from another authorized network/IP instead of forcing the route.
4. Save artifacts under the lab, e.g. `~/browser-tools-lab/scripts/` and `~/browser-tools-lab/outputs/<mission>/`, so later sessions can inspect scripts, JSONL, summaries, and reports.
5. For fallback public sources, label them clearly as fallback/non-official and filter inactive/expired listings before presenting them as candidate jobs.

## AMS-specific findings from the probe

- `https://www.ams.at/` was reachable.
- Official job links discovered from AMS pages included:
  - `https://jobs.ams.at/public/emps/`
  - `https://jobs.ams.at/public/emps/jobs`
  - `https://jobs.ams.at`
  - `https://jobroom.ams.or.at/jobsuche/Suche.jsp`
  - `https://jobroom.ams.or.at/jobroom/index_as.jsp`
- AMS robots.txt disallowed several search/client paths on `www.ams.at`, including `/arbeitssuchende/suche` and `/client`; these should not be crawled.
- From the VPS used in the session, `jobs.ams.at` and `jobroom.ams.or.at` DNS resolved but TCP 443/curl requests timed out or appeared closed. This is a reachability condition, not proof AMS has no jobs.
- browser-use could open the AMS homepage and begin the “Alle Jobs” route, but the job-search tab stalled when the underlying job hosts were unreachable.
- Scrapy discovery produced zero AMS records because no reachable allowed job endpoint was confirmed.

## Script/output pattern used

Example locations from the session:

- browser-use probe: `/home/ubuntu/browser-tools-lab/scripts/browser_use_ams_test.py`
- Scrapy discovery: `/home/ubuntu/browser-tools-lab/scripts/ams_seasonal_agriculture_search.py`
- report/output folder: `/home/ubuntu/browser-tools-lab/outputs/ams-seasonal-agriculture/`

## Reporting pattern

When presenting results, distinguish:

- **tested and reachable**
- **tested but blocked/unreachable**
- **robots/login/anti-bot restricted**
- **official source vs fallback source**
- **verified active postings vs expired/inactive listings**

Do not claim “no jobs exist” when the evidence is only “the official job host was unreachable from this network.”
