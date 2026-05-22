---
name: browser-automation-tool-evaluation
description: Evaluate, install, and benchmark free/open-source browser operation and crawling tools in isolated labs, with dependency checks and user-preference constraints.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [browser-automation, crawling, scraping, evaluation, isolation, benchmarking]
    created_by: agent
---

# Browser Automation Tool Evaluation

## Purpose

Use this skill when the user asks to choose, compare, install, or benchmark browser automation, human-like browsing, crawling, or scraping tools.

This is a class-level workflow for keeping browser-control experiments isolated, dependency-aware, and reversible before wiring anything into Hermes core.

## User preference signals

- If Ayman says Playwright or Puppeteer are too heavy/buggy, do not recommend them as the primary foundation.
- Do not silently reintroduce Playwright/Puppeteer through a “wrapper” recommendation. Verify lockfiles or package metadata before claiming a tool avoids them.
- Prefer free/open-source tools first.
- Separate “human-like browser operation” from “crawling/scraping”; one tool rarely does both well.
- For Ayman's Hermes work, prefer the proven `browser-use` + `Scrapy` split over native Hermes browser/crawling tools unless he explicitly asks otherwise or the task cannot be done from the isolated lab.

## Recommended split under a no-Playwright/no-Puppeteer constraint

- Human-like browser operation: `browser-use` as the first candidate to test, because it is AI-native, Python-based, MIT licensed, and currently installs around `cdp-use` rather than Playwright/Puppeteer packages.
- Crawling/scraping: `Scrapy`, because it is mature, BSD-3-Clause licensed, Python-based, and does not require a browser engine by default.
- Fallback human-browser candidate: `SeleniumBase` only if `browser-use` disappoints; check optional dependencies carefully because it advertises Playwright integration but does not require it for the Selenium/CDP path.

## Phase 1 — Inspect before installing

Run read-only checks first:

```bash
python3 --version
python3 -m pip --version || true
command -v uv && uv --version || true
command -v chromium && chromium --version || true
command -v google-chrome && google-chrome --version || true
command -v firefox && firefox --version || true
```

Check upstream dependency metadata before recommending a stack:

```bash
python3 - <<'PY'
import urllib.request
for name, url in {
  'browser-use': 'https://raw.githubusercontent.com/browser-use/browser-use/main/pyproject.toml',
  'scrapy': 'https://raw.githubusercontent.com/scrapy/scrapy/master/pyproject.toml',
}.items():
    txt = urllib.request.urlopen(url, timeout=20).read().decode('utf-8', 'replace').lower()
    print(name, 'playwright=', 'playwright' in txt, 'puppeteer=', 'puppeteer' in txt, 'selenium=', 'selenium' in txt, 'cdp=', 'cdp' in txt)
PY
```

## Phase 2 — Install in an isolated lab

Never install candidate browser tooling directly into Hermes core first. Use separate virtual environments:

```bash
mkdir -p ~/browser-tools-lab/{browser-use,scrapy,outputs,scripts}
uv venv --python 3.12 ~/browser-tools-lab/browser-use/.venv
uv venv --python 3.12 ~/browser-tools-lab/scrapy/.venv
uv pip install --python ~/browser-tools-lab/browser-use/.venv/bin/python browser-use
uv pip install --python ~/browser-tools-lab/scrapy/.venv/bin/python scrapy
uv pip freeze --python ~/browser-tools-lab/browser-use/.venv/bin/python > ~/browser-tools-lab/browser-use/requirements.lock
uv pip freeze --python ~/browser-tools-lab/scrapy/.venv/bin/python > ~/browser-tools-lab/scrapy/requirements.lock
```

Pitfall: `uv venv` may create a venv without `pip`; use `uv pip install --python <venv>/bin/python ...` instead of assuming `<venv>/bin/pip` exists.

## Phase 3 — Verify forbidden dependencies

For no-Playwright/no-Puppeteer setups, verify both lockfiles:

```bash
grep -Ei '^(playwright|puppeteer|pyppeteer)==' \
  ~/browser-tools-lab/browser-use/requirements.lock \
  ~/browser-tools-lab/scrapy/requirements.lock \
  || echo 'No forbidden deps found'
```

If a forbidden dependency appears, stop and report it plainly before continuing.

## Phase 4 — Smoke test without credentials

Do not start with real accounts, cookies, or sensitive sessions.

For browser-use, first do an import/version smoke test before any live browser task.
For Scrapy, crawl a local static fixture first so network flakiness does not hide install failures.

See `references/browser-use-scrapy-lab-2026-05.md` for a concrete lab layout and smoke-test scripts from a successful session.

For job-site missions, use the access/robots → browser route → crawler extraction sequence in `references/ams-seasonal-agriculture-job-search-2026-05.md`; it captures the AMS seasonal agriculture probe pattern and how to report official-source blockers versus fallback listings.

## Phase 5 — Benchmark before integration

Only after smoke tests pass, run a small benchmark:

1. Human-like browser tool opens a public docs page and extracts install steps.
2. Human-like browser tool opens a GitHub repo and extracts stars/license/issues.
3. Crawler follows a small documentation section and writes JSONL.
4. Crawler follows same-domain links with a depth/page limit.
5. Confirm no real credentials, browser cookies, or private profiles were touched.

For browser-use with OpenCode Go models, prefer the known-good path from the lab before trying other models:

- model: `kimi-k2.6`
- set `dont_force_structured_output=True` when structured JSON mode is brittle
- Chromium path observed on the VPS: `/snap/bin/chromium`

Do not encode a temporary model failure as “browser-use is broken”; switch model/structured-output settings and rerun a small public benchmark.

## Safety and rollback

- Keep lab paths outside Hermes core, e.g. `~/browser-tools-lab`.
- Lockfiles must be saved for reproducibility.
- If the lab fails, remove only the lab directory after confirmation:

```bash
rm -rf ~/browser-tools-lab
```

This touches installed files; confirm before deleting.

## Common System Alerts

- `No module named pip` inside a uv-created venv: use `uv pip install --python <venv>/bin/python`.
- Browser-control tool imports pass but live tasks fail: do not treat that as install failure; run a separate benchmark and inspect browser/profile/model configuration.
- Crawling a public site fails: retest against a local fixture before blaming Scrapy.
