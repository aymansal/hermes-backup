# Browser-use + Scrapy isolated lab — 2026-05

## Session context

The user wanted two free/open-source tools:

- one for human-like browser operation: click, type, navigate like a human;
- one for crawling/scraping;
- explicitly avoiding Playwright and Puppeteer because the user considers them heavy/buggy.

## Research outcome

Initial candidates included browser-use, Crawlee, Scrapy, SeleniumBase, Skyvern, Stagehand, AgentQL, and LaVague.

After the no-Playwright/no-Puppeteer constraint, the selected pair was:

- `browser-use` for human-like browser operation;
- `Scrapy` for crawling/scraping.

Rationale:

- `browser-use` is MIT licensed, Python-based, AI-native, active, and installed without Playwright/Puppeteer packages in this lab. It did install `cdp-use==1.4.5`.
- `Scrapy` is BSD-3-Clause licensed, mature, Python-based, and does not require browser engines by default.
- `Crawlee` was deprioritized because its ecosystem commonly uses Playwright/Puppeteer even though it can use lighter crawlers.

## Lab layout used

```text
/home/ubuntu/browser-tools-lab/
  README.md
  browser-use/
    .venv/
    requirements.lock
  scrapy/
    .venv/
    requirements.lock
    sample-site/
      index.html
      page2.html
  scripts/
    browser_use_smoke.py
    scrapy_smoke.py
  outputs/
    scrapy-smoke.jsonl
```

## Install commands used

`uv venv` created venvs without pip, so `uv pip --python` was used.

```bash
mkdir -p /home/ubuntu/browser-tools-lab/{browser-use,scrapy,outputs,scripts}
uv venv --python 3.12 /home/ubuntu/browser-tools-lab/browser-use/.venv
uv venv --python 3.12 /home/ubuntu/browser-tools-lab/scrapy/.venv
uv pip install --python /home/ubuntu/browser-tools-lab/browser-use/.venv/bin/python browser-use
uv pip install --python /home/ubuntu/browser-tools-lab/scrapy/.venv/bin/python scrapy
uv pip freeze --python /home/ubuntu/browser-tools-lab/browser-use/.venv/bin/python > /home/ubuntu/browser-tools-lab/browser-use/requirements.lock
uv pip freeze --python /home/ubuntu/browser-tools-lab/scrapy/.venv/bin/python > /home/ubuntu/browser-tools-lab/scrapy/requirements.lock
```

Installed versions observed:

```text
browser-use==0.12.7
cdp-use==1.4.5
scrapy==2.16.0
```

Forbidden dependency verification:

```bash
grep -Ei '^(playwright|puppeteer|pyppeteer)==' \
  /home/ubuntu/browser-tools-lab/browser-use/requirements.lock \
  /home/ubuntu/browser-tools-lab/scrapy/requirements.lock \
  || echo 'No forbidden deps found'
```

Result: no forbidden deps found.

## Smoke script: browser-use import

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.metadata as md
from browser_use import Agent, Browser, BrowserProfile, ChatOpenAI

print('browser-use version:', md.version('browser-use'))
print('Agent:', Agent.__name__)
print('Browser:', Browser.__name__)
print('BrowserProfile:', BrowserProfile.__name__)
print('ChatOpenAI:', ChatOpenAI.__name__)
print('smoke: ok')
```

Expected result:

```text
browser-use version: 0.12.7
Agent: Agent
Browser: BrowserSession
BrowserProfile: BrowserProfile
ChatOpenAI: ChatOpenAI
smoke: ok
```

## Smoke script: Scrapy local fixture crawl

Use a local two-page static site to avoid external site/network noise.

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider

ROOT = Path('/home/ubuntu/browser-tools-lab')
SITE = ROOT / 'scrapy' / 'sample-site'
OUT = ROOT / 'outputs' / 'scrapy-smoke.jsonl'

SITE.mkdir(parents=True, exist_ok=True)
(SITE / 'index.html').write_text('''<!doctype html>
<html><head><title>Dungeon Index</title></head>
<body>
<h1>Dungeon Index</h1>
<a href="page2.html">Second chamber</a>
</body></html>
''', encoding='utf-8')
(SITE / 'page2.html').write_text('''<!doctype html>
<html><head><title>Second Chamber</title></head>
<body><h1>Second Chamber</h1><p>Crawl smoke passed.</p></body></html>
''', encoding='utf-8')
if OUT.exists():
    OUT.unlink()

class LocalSpider(Spider):
    name = 'local_smoke'
    start_urls = [(SITE / 'index.html').as_uri()]
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'FEEDS': {str(OUT): {'format': 'jsonlines', 'overwrite': True}},
        'ROBOTSTXT_OBEY': False,
    }

    def parse(self, response):
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'h1': response.css('h1::text').get(),
        }
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, self.parse)

process = CrawlerProcess(settings={'LOG_LEVEL': 'ERROR'})
process.crawl(LocalSpider)
process.start()

rows = [json.loads(line) for line in OUT.read_text(encoding='utf-8').splitlines() if line.strip()]
print('scrapy rows:', len(rows))
for row in rows:
    print(row)
assert len(rows) == 2, rows
assert {row['title'] for row in rows} == {'Dungeon Index', 'Second Chamber'}, rows
print('smoke: ok')
```

Expected result:

```text
scrapy rows: 2
... Dungeon Index ...
... Second Chamber ...
smoke: ok
```

## Live benchmark results

After smoke tests, both Gates passed public real-world benchmarks:

- browser-use opened `github.com/scrapy/scrapy` and extracted `repo=scrapy/scrapy`, `stars=61.8k`, `license=BSD-3-Clause`.
- Scrapy crawled `docs.scrapy.org/en/latest/intro/`, followed same-domain links with a small page cap, and wrote 5 JSONL rows.

Observed output paths in the lab:

```text
/home/ubuntu/browser-tools-lab/outputs/browser-use-benchmark.txt
/home/ubuntu/browser-tools-lab/outputs/scrapy-docs-benchmark.jsonl
/home/ubuntu/browser-tools-lab/BENCHMARK_REPORT.md
```

## Browser-use model quirk

A browser-use run with `glm-5.1` failed because the model returned empty/invalid structured output. The durable fix was not to treat the tool as broken; rerun with a model/settings combo that handles the task:

```text
model: kimi-k2.6
provider/base: OpenCode Go-compatible OpenAI route
setting: dont_force_structured_output=True
chromium: /snap/bin/chromium
```

## Standing operational preference

For Ayman, future browser/crawling tasks should default to:

- `browser-use` for human-like browser operation;
- `Scrapy` for crawling/scraping;
- native Hermes browser/crawling tools only as fallback or when explicitly requested.

## Lessons

- For this user, avoid recommending Playwright/Puppeteer-first stacks unless explicitly requested or strongly justified.
- Always verify actual installed dependencies; do not rely only on README descriptions.
- Keep browser-operation and crawling as separate Gates.
- Start with import/local-fixture smoke tests before real web benchmarks.
- When a browser-use model fails structured output, capture the working model/settings combination instead of hardening the transient failure into a negative rule.
