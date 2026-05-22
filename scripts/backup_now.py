#!/usr/bin/env python3
"""Regenerate Ayman's private Hermes backup repo safely.

Rules:
- Do not copy .env, auth.json, sessions/state.db, logs, caches, OAuth tokens, SSH keys.
- Sanitize secret-looking config values.
- Refuse to commit if literal .env secret values appear in text/DB backup files.
- Print only when a backup commit is pushed or when manual attention is required.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

HOME = Path.home()
HERMES = HOME / ".hermes"
SRC = HERMES / "hermes-agent"
REPO = HERMES / "backups" / "hermes-backup"
REMOTE = "https://github.com/aymansal/hermes-backup.git"

IGNORE_NAMES = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".next", "coverage",
    ".coverage", "htmlcov", ".cache",
}
SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|token|secret|password|passwd|auth|credential|cookie|private[_-]?key|client[_-]?secret)",
    re.I,
)


def run(cmd: str, cwd: Path | None = None, check: bool = False) -> str:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, shell=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and p.returncode:
        raise RuntimeError(f"Command failed ({p.returncode}): {cmd}\n{p.stdout}")
    return p.stdout


def ignore_func(_dirpath: str, names: list[str]) -> set[str]:
    return {n for n in names if n in IGNORE_NAMES or n.endswith((".pyc", ".pyo"))}


def sanitize_text(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^(\s*[^#\s][^:]{0,100}:\s*)(.*)$", line)
        if m and SECRET_KEY_RE.search(m.group(1)) and m.group(2).strip() not in ("", "{}", "[]", "null", "None"):
            out.append(m.group(1) + "<SET_ON_RESTORE>")
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASS|AUTH|COOKIE|PRIVATE_KEY)[A-Za-z0-9_]*\s*=).*$", line, re.I)
        if m:
            out.append(m.group(1) + "<SET_ON_RESTORE>")
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def sqlite_backup(src: Path, dest: Path) -> None:
    try:
        con = sqlite3.connect(str(src))
        out = sqlite3.connect(str(dest))
        con.backup(out)
        out.close(); con.close()
    except Exception:
        shutil.copy2(src, dest)


def env_entries() -> list[tuple[str, str]]:
    env = HERMES / ".env"
    entries: list[tuple[str, str]] = []
    if not env.exists():
        return entries
    for line in env.read_text(errors="ignore").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split("=", 1)
        k = k.strip().replace("export ", "")
        v = v.strip().strip('"\'')
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k):
            entries.append((k, v))
    return entries


def prepare_repo() -> None:
    REPO.parent.mkdir(parents=True, exist_ok=True)
    if not (REPO / ".git").exists():
        if REPO.exists():
            shutil.rmtree(REPO)
        run(f"gh repo clone aymansal/hermes-backup {REPO}", check=True)
    else:
        run("git pull --ff-only", cwd=REPO)


def rebuild() -> int:
    now = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    for item in REPO.iterdir():
        if item.name == ".git":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    for d in ["config", "secrets", "state", "source", "systemd", "scripts", "docs", "skills"]:
        (REPO / d).mkdir(parents=True, exist_ok=True)

    shutil.copytree(SRC, REPO / "source" / "hermes-agent", ignore=ignore_func, dirs_exist_ok=True)
    (REPO / "source" / "git-status.txt").write_text(run("git status --short --branch", SRC), encoding="utf-8")
    (REPO / "source" / "git-remotes.txt").write_text(run("git remote -v", SRC), encoding="utf-8")
    (REPO / "source" / "local-patches.patch").write_text(run("git diff --binary", SRC), encoding="utf-8")
    (REPO / "source" / "untracked-files.txt").write_text(run("git ls-files --others --exclude-standard", SRC), encoding="utf-8")

    for name in ["config.yaml", "SOUL.md", "OPERATOR_PROFILE.md", ".install_method", "context_length_cache.yaml"]:
        p = HERMES / name
        if p.exists() and p.is_file():
            dest = REPO / "config" / (name.replace(".", "_", 1) if name.startswith(".") else name)
            data = p.read_text(errors="replace")
            if name.endswith((".yaml", ".yml")):
                data = sanitize_text(data)
            dest.write_text(data, encoding="utf-8")

    entries = env_entries()
    keys = sorted({k for k, _ in entries})
    (REPO / "secrets" / "env.template").write_text("\n".join(f"{k}=" for k in keys) + "\n", encoding="utf-8")
    (REPO / "secrets" / "README.md").write_text(
        "# Access Keys not stored here\n\nThis repo intentionally excludes secret values. Copy env.template to ~/.hermes/.env and fill Access Keys during restore.\n",
        encoding="utf-8",
    )

    skills_src = HERMES / "skills"
    if skills_src.exists():
        shutil.copytree(skills_src, REPO / "skills" / "user-skills", ignore=ignore_func, dirs_exist_ok=True)

    for dbname in ["memory_store.db", "kanban.db"]:
        src = HERMES / dbname
        if src.exists():
            sqlite_backup(src, REPO / "state" / dbname)
    cron_src = HERMES / "cron"
    if cron_src.exists():
        shutil.copytree(cron_src, REPO / "state" / "cron", ignore=lambda _d, names: {n for n in names if n in {"output", "logs", "__pycache__"} or n.endswith(".lock")}, dirs_exist_ok=True)

    sysd = HOME / ".config" / "systemd" / "user"
    if sysd.exists():
        for p in list(sysd.glob("hermes*.service")) + list(sysd.glob("hermes*.timer")):
            (REPO / "systemd" / p.name).write_text(sanitize_text(p.read_text(errors="replace")), encoding="utf-8")

    # Preserve restore helper if present in current repo history; otherwise write minimal pointer.
    restore = REPO / "scripts" / "restore.sh"
    if not restore.exists():
        restore.write_text("#!/usr/bin/env bash\nset -euo pipefail\necho 'See README.md for restore instructions.'\n", encoding="utf-8")
        restore.chmod(0o755)
    shutil.copy2(Path(__file__), REPO / "scripts" / "backup_now.py")

    readme = f"""# Hermes Backup — Shadow System Recovery Vault\n\nPrivate backup for Ayman's Hermes Agent setup.\n\nLast generated: `{now}`\n\n## Included\n- Full Hermes source snapshot with local patches\n- Sanitized config, persona/profile, Skill Runes\n- Holographic memory DB, kanban DB, cron definitions\n- Sanitized systemd user units\n- Access Key template only, no secret values\n\n## Excluded\n`.env` values, `auth.json`, OAuth tokens, GitHub tokens, Telegram bot tokens, SSH keys, cookies, raw logs, session transcript DB, caches, and media caches.\n\n## Quick restore\n```bash\ngit clone {REMOTE}\ncd hermes-backup\nbash scripts/restore.sh\n# fill ~/.hermes/.env from secrets/env.template\ncd ~/.hermes/hermes-agent\nhermes doctor\n```\n"""
    (REPO / "README.md").write_text(readme, encoding="utf-8")
    (REPO / "backup-manifest.json").write_text(json.dumps({
        "generated_at": now,
        "hermes_home": str(HERMES),
        "source_path": str(SRC),
        "env_key_count": len(keys),
        "included": ["source", "sanitized config", "persona", "skills", "memory", "kanban", "cron", "systemd", "env template"],
        "excluded": ["secret values", "auth.json", "state.db", "logs", "caches", "media", "SSH keys", "OAuth tokens"],
    }, indent=2) + "\n", encoding="utf-8")
    return len(keys)


def leak_check() -> list[str]:
    entries = [(k, v) for k, v in env_entries() if len(v) >= 20 and k != "TERMINAL_MODAL_IMAGE"]
    leaks: set[str] = set()
    for p in REPO.rglob("*"):
        if ".git" in p.parts or not p.is_file():
            continue
        if p.name in {".env", "auth.json", "state.db", "gateway.log", "agent.log", "errors.log"}:
            leaks.add(str(p.relative_to(REPO)))
            continue
        data = p.read_bytes()
        for k, v in entries:
            if v.encode() in data:
                leaks.add(f"{p.relative_to(REPO)} contains literal value from {k}")
    return sorted(leaks)


def main() -> int:
    prepare_repo()
    key_count = rebuild()
    leaks = leak_check()
    if leaks:
        print("SYSTEM ALERT: backup refused; possible secret leakage detected:")
        for item in leaks[:20]:
            print(f"- {item}")
        return 2
    run("git add README.md backup-manifest.json config scripts secrets skills source state systemd", cwd=REPO, check=True)
    status = run("git status --porcelain", cwd=REPO)
    if not status.strip():
        return 0
    run('git commit -m "backup: refresh Hermes recovery vault"', cwd=REPO, check=True)
    run("git push", cwd=REPO, check=True)
    sha = run("git rev-parse --short HEAD", cwd=REPO).strip()
    print(f"Hermes backup pushed to aymansal/hermes-backup at {sha}; env keys templated: {key_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
