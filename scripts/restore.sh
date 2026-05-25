#!/usr/bin/env bash
# Restore Ayman's Hermes recovery vault onto a fresh VPS.
# Secret values are intentionally NOT in this repo. Fill ~/.hermes/.env after restore.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
ASSUME_YES=0
SKIP_PACKAGES=0
SKIP_SOURCE=0
SKIP_SYSTEMD=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Hermes Restore Script — Shadow System Recovery

Usage:
  bash scripts/restore.sh [options]

Options:
  --yes             Do not ask before overwriting existing restore targets.
  --dry-run         Show what would be restored, but do not write files.
  --skip-packages   Do not install apt packages.
  --skip-source     Do not restore source/hermes-agent.
  --skip-systemd    Do not restore user systemd units.
  -h, --help        Show this help.

After restore:
  1. Fill ~/.hermes/.env with Access Keys.
  2. Re-login OAuth providers if needed, e.g. hermes login --provider openai-codex.
  3. Run: cd ~/.hermes/hermes-agent && hermes doctor
  4. Start gateway only after keys are ready.
EOF
}

log() { printf '\033[1;34m[restore]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[fail]\033[0m %s\n' "$*" >&2; exit 1; }
run() {
  if [ "$DRY_RUN" = 1 ]; then
    printf '[dry-run] %q ' "$@"; printf '\n'
  else
    "$@"
  fi
}
confirm_overwrite() {
  if [ "$ASSUME_YES" = 1 ] || [ "$DRY_RUN" = 1 ]; then
    return 0
  fi
  cat <<EOF
This will restore files into:
  $HERMES_HOME
  $SYSTEMD_USER_DIR

Existing config/source/skills/state files may be overwritten.
Secret files like ~/.hermes/.env and ~/.hermes/auth.json will NOT be overwritten.
EOF
  read -r -p "Continue? Type YES to proceed: " answer
  [ "$answer" = "YES" ] || fail "Restore cancelled."
}

while [ $# -gt 0 ]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --skip-packages) SKIP_PACKAGES=1 ;;
    --skip-source) SKIP_SOURCE=1 ;;
    --skip-systemd) SKIP_SYSTEMD=1 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown option: $1" ;;
  esac
  shift
done

[ -d "$ROOT" ] || fail "Cannot find restore root."
[ -d "$ROOT/config" ] || fail "Missing config/ directory. Run this from the cloned hermes-backup repo."
[ -d "$ROOT/source/hermes-agent" ] || fail "Missing source/hermes-agent/ directory in backup."

log "Restore root: $ROOT"
log "Hermes home:  $HERMES_HOME"

confirm_overwrite

if [ "$SKIP_PACKAGES" = 0 ]; then
  if command -v apt-get >/dev/null 2>&1; then
    log "Installing base packages if missing."
    run sudo apt-get update
    run sudo apt-get install -y git curl rsync sqlite3 python3 python3-venv python3-pip build-essential
  else
    warn "apt-get not found; skipping package install."
  fi
fi

log "Creating directories."
run mkdir -p "$HERMES_HOME" "$SYSTEMD_USER_DIR"

log "Restoring sanitized config/persona files."
run rsync -a "$ROOT/config/" "$HERMES_HOME/"
if [ -f "$HERMES_HOME/_install_method" ] && [ ! -f "$HERMES_HOME/.install_method" ]; then
  run mv "$HERMES_HOME/_install_method" "$HERMES_HOME/.install_method"
fi

if [ "$SKIP_SOURCE" = 0 ]; then
  log "Restoring Hermes source snapshot."
  if [ -d "$HERMES_HOME/hermes-agent" ]; then
    stamp="$(date +%Y%m%d-%H%M%S)"
    warn "Existing hermes-agent directory found; moving to hermes-agent.before-restore-$stamp"
    run mv "$HERMES_HOME/hermes-agent" "$HERMES_HOME/hermes-agent.before-restore-$stamp"
  fi
  run mkdir -p "$HERMES_HOME/hermes-agent"
  run rsync -a "$ROOT/source/hermes-agent/" "$HERMES_HOME/hermes-agent/"
fi

if [ -d "$ROOT/skills/user-skills" ]; then
  log "Restoring Skill Runes."
  run mkdir -p "$HERMES_HOME/skills"
  run rsync -a "$ROOT/skills/user-skills/" "$HERMES_HOME/skills/"
fi

if [ -d "$ROOT/state" ]; then
  log "Restoring memory/kanban/cron state."
  run rsync -a "$ROOT/state/" "$HERMES_HOME/"
fi

if [ "$SKIP_SYSTEMD" = 0 ] && [ -d "$ROOT/systemd" ]; then
  log "Restoring systemd user units."
  run rsync -a "$ROOT/systemd/" "$SYSTEMD_USER_DIR/"
  run systemctl --user daemon-reload || warn "systemctl --user daemon-reload failed; run it manually after login/session setup."
fi

if [ ! -f "$HERMES_HOME/.env" ]; then
  if [ -f "$ROOT/secrets/env.template" ]; then
    log "Creating ~/.hermes/.env from template. Fill Access Keys before starting services."
    run cp "$ROOT/secrets/env.template" "$HERMES_HOME/.env"
    run chmod 600 "$HERMES_HOME/.env"
  else
    warn "No secrets/env.template found; create $HERMES_HOME/.env manually."
  fi
else
  warn "$HERMES_HOME/.env already exists; not overwriting secrets."
fi

run chmod 700 "$HERMES_HOME" || true
run chmod 600 "$HERMES_HOME/config.yaml" 2>/dev/null || true
run chmod 600 "$HERMES_HOME/memory_store.db" 2>/dev/null || true
run chmod 600 "$HERMES_HOME/kanban.db" 2>/dev/null || true

log "Restore copy complete."

if [ "$DRY_RUN" = 1 ]; then
  log "Dry-run complete; skipped hermes doctor."
elif command -v hermes >/dev/null 2>&1; then
  log "Running hermes doctor."
  (cd "$HERMES_HOME/hermes-agent" && hermes doctor) || warn "hermes doctor reported issues. Usually missing Access Keys/OAuth login."
else
  warn "hermes CLI not found in PATH. Install Hermes or open a new shell, then run: cd $HERMES_HOME/hermes-agent && hermes doctor"
fi

cat <<EOF

Next commands:
  nano $HERMES_HOME/.env
  cd $HERMES_HOME/hermes-agent
  hermes doctor

If using Codex/OAuth providers, re-login on this VPS:
  hermes login --provider openai-codex

Start the Comms Gate only after Access Keys are ready:
  loginctl enable-linger "$USER"
  systemctl --user daemon-reload
  systemctl --user enable --now hermes-gateway
  systemctl --user status hermes-gateway --no-pager -n 50

System note: secrets were not restored. No key, no summon.
EOF
